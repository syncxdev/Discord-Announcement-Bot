import discord
import json

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
        color=discord.Color.red()
    )
    embed.set_footer(text=f'Autor: {message.author}', icon_url=message.author.avatar.url)
    embed.timestamp = message.created_at

    channel = message.guild.get_channel(int(channel_id))
    if channel and isinstance(channel, discord.TextChannel):
        await channel.send(embed=embed)

client.run(TOKEN)
