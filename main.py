# -*- coding: utf-8 -*-
import discord
import youtube_dl
from discord.ext import commands
import asyncio
import time

# Configurando o bot
token = "NjExNTgwMTkyMDExNTgzNDg5.GZkrZn.swTlbR164LM3BY5VebAoz6r68TfLJ-1LmPwZ78"
prefix = "!!"
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

# Variavel para rastrear o tempo desde a último comando de música
last_music_command_time = 0


# Dizendo ao usuário que o bot se conectou com sucesso ao servidor
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')


# Implementando o bot para tocar música do YouTube
@bot.command()
async def play(ctx, url: str):
    # Atualiza o tempo do comando da última música tocada
    global last_music_command_time
    last_music_command_time = time.time()
    # Verifica se o usuário está em um canal de voz
    if not ctx.author.voice:
        await ctx.send("Você tem que estar em um canal de voz para usar este comando.")
        return

    # Obtém o canal de voz no qual o autor do comando está atualmente conectado
    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()

    # Faz o download do áudio do YouTube
    audio_options = {"format": "bestaudio/best", "postprocessor": [
        {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]}
    with youtube_dl.YoutubeDL(audio_options) as audio:
        info = audio.extract_info(url, download=False)
        ur12 = info["formats"][0]["url"]

    # Reproduz o audio no canal de voz
    voice_client.play(discord.FFmpegPCMAudio(ur12))


@bot.command()
async def leave(ctx):
    # Verifica se o bot está em um canal de voz
    if ctx.voice_client:
        voice_client = ctx.voice_client

        members = voice_client.channel.members  # Obtém os usuários que estão no canal de voz

        # Verifica se tem somente um usuário no canal de voz (O próprio bot)
        if len(members) == 1 and voice_client.is_connected():
            await voice_client.disconnect()
            await ctx.send("O bot foi desconectado por não ter usuários no canal de voz.")
        else:
            await ctx.send("Existem usuários no canal de voz.")

        # Reseta o tempo do comando da última música tocada
        global last_music_command_time
        last_music_command_time = 0


@bot.event
async def on_message(message):
    # Verifica se o comando é relacionado a música
    if message.content.startswith(prefix + "play"):
        # Atualiza o tempo do comando da última música tocada
        global last_music_command_time
        last_music_command_time = time.time()

    await bot.process_commands(message)


async def check_music_inactivity():
    global last_music_command_time

    while True:
        # Verificia o tempo do último comando de música é maior que um determinado limite
        if time.time() - last_music_command_time > 300:  # Tempo em segundos (5 minutos)
            # Desconecta o bot do canal de voz
            voice_client = discord.utils.get(bot.voice_clients)
            if voice_client:
                members = voice_client.channel.members  # Obtém os usuários que estão no canal de voz

                # Verifica se tem somente um usuário no canal de voz (O próprio bot)
                if len(members) == 1 and voice_client.is_connected():
                    await voice_client.disconnect()
                    print("Bot foi desconectado por inatividade.")

                    last_music_command_time = 0

        await asyncio.sleep(60)


# Inicia o bot
bot.run(token)
