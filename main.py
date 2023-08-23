import discord
import json
import asyncio

intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)

with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config['token']
archive_channel_id = config.get('archive_channel')

channels = config['channels']

repeat_tasks = {}  # Dictionary to store repeat tasks for each channel

@client.event
async def on_ready():
    print('Der Bot ist bereit.')
    for channel_id, channel_data in channels.items():
        repeat_enabled = channel_data.get('repeat', {}).get('enabled', False)
        if repeat_enabled:
            interval = channel_data['repeat']['interval']
            channel = client.get_channel(int(channel_id))
            repeat_tasks[channel_id] = asyncio.create_task(repeat_announcement(channel, channel_data, interval))

async def archive_announcement(channel_name, message_url):
    if archive_channel_id and archive_channel_id != "archive_channel_id_here":
        archive_channel = client.get_channel(int(archive_channel_id))
        if archive_channel and isinstance(archive_channel, discord.TextChannel):
            archive_message = await archive_channel.send(f'Archiviert von {channel_name}: {message_url}')

async def repeat_announcement(channel, channel_data, interval):
    while True:
        await asyncio.sleep(interval)
        last_message = await channel.history(limit=1).flatten()[-1]
        if not last_message.author.bot:
            await archive_announcement(channel_data['name'], last_message.jump_url)
            
            embed = create_embed(channel_data)
            embed.description = last_message.content

            sent_message = await channel.send(embed=embed)

            message_duration = channel_data.get('message_duration', 0)
            if message_duration > 0:
                await asyncio.sleep(message_duration)
                await sent_message.delete()

            auto_reactions = channel_data.get('auto_reactions', [])
            for reaction in auto_reactions:
                await sent_message.add_reaction(reaction)

@client.event
async def on_message(message):
    if message.author.bot or str(message.channel.id) not in channels:
        return

    channel_id = str(message.channel.id)
    channel_data = channels[channel_id]

    embed = create_embed(channel_data)

    if channel_data.get('formatting', False):
        embed.description = f"*{message.content}*"

    show_server_icon = channel_data.get('show_server_icon', False)
    if show_server_icon and message.guild:
        server_icon_url = message.guild.icon_url
        if server_icon_url:
            server_icon_url = server_icon_url_as_round(server_icon_url)
            embed.set_thumbnail(url=server_icon_url)

    embed.set_footer(text=f'Autor: {message.author}' if not message.author.bot else "", icon_url=message.author.avatar_url if message.author.avatar_url and not message.author.bot else None)
    embed.timestamp = message.created_at

    channel = message.guild.get_channel(int(channel_id))
    if channel and isinstance(channel, discord.TextChannel):
        sent_message = await channel.send(embed=embed)
        
        message_duration = channel_data.get('message_duration', 0)
        if message_duration > 0:
            await asyncio.sleep(message_duration)
            await sent_message.delete()

        if archive_channel_id and archive_channel_id != "archive_channel_id_here":
            await archive_announcement(channel_data['name'], sent_message.jump_url)

        auto_reactions = channel_data.get('auto_reactions', [])
        for reaction in auto_reactions:
            await sent_message.add_reaction(reaction)

def create_embed(channel_data):
    title = channel_data['title']
    description = channel_data.get('description', '')
    color = channel_data.get('color', 0x3498db)  # Standardfarbe, falls nicht angegeben
    
    if isinstance(color, str) and color.startswith('#'):
        color = int(color[1:], 16)
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed

def server_icon_url_as_round(icon_url):
    return f'{icon_url}?size=1024&radius=512'

client.run(TOKEN)
