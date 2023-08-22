import discord
import json
import asyncio

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config['token']
channels = config['channels']

@client.event
async def on_ready():
    print('Der Bot ist bereit.')

@client.event
async def on_message(message):
    if message.author.bot or str(message.channel.id) not in channels:
        return

    channel_id = str(message.channel.id)
    channel_data = channels[channel_id]

    embed = discord.Embed(
        title=channel_data['title'],
        description=message.content,
        color=int(channel_data.get('color', '0x3498db'), 16)
    )

    if channel_data.get('formatting', False):
        embed.description = f"*{message.content}*"

    show_server_icon = channel_data.get('show_server_icon', False)
    if show_server_icon and message.guild:
        server_icon_url = message.guild.icon_url
        if server_icon_url:
            embed.set_thumbnail(url=server_icon_url)

    embed.set_footer(text=f'Autor: {message.author}', icon_url=message.author.avatar.url)
    embed.timestamp = message.created_at

    channel = message.guild.get_channel(int(channel_id))
    if channel and isinstance(channel, discord.TextChannel):
        sent_message = await channel.send(embed=embed)
        
        message_duration = channel_data.get('message_duration', 0)
        if message_duration > 0:
            await asyncio.sleep(message_duration)
            await sent_message.delete()

        archive_channel_id = channel_data.get('archive_channel', None)
        if archive_channel_id and archive_channel_id != "archive_channel_id_here":
            archive_channel = message.guild.get_channel(int(archive_channel_id))
            if archive_channel and isinstance(archive_channel, discord.TextChannel):
                await archive_channel.send(embed=embed)

        auto_reactions = channel_data.get('auto_reactions', [])
        for reaction in auto_reactions:
            await sent_message.add_reaction(reaction)

client.run(TOKEN)

