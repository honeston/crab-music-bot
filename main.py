import discord
import logging
from Config import *
from MusicDataSet import MusicData
from PlayController import playController
from YoutubeDataAPI import youtubeDataAPI

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class MyClient(discord.Client):

    # 準備完了
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
    
    # メッセージ受信
    async def on_message(self, message):
        if message.author == client.user:
            return

        print('Message from {0.author}: {0.content}'.format(message))

        content = message.content
        contentList = content.split(' ')

        # post
        if len(contentList) >= 2 and (contentList[0] == '-p' or contentList[0] == '-post'):
            if message.author.voice is None:
                await message.channel.send("You are not connected to a voice channel.")
                return

            if message.guild.voice_client is None:
                # ボイスチャンネルに接続する
                await message.author.voice.channel.connect()
                await message.channel.send("connected")

            await self.popCommand(message,contentList)

        # join
        if content == '-join':
            if message.author.voice is None:
                await message.channel.send("You are not connected to a voice channel.")
                return

            # ボイスチャンネルに接続する
            await message.author.voice.channel.connect()
            await message.channel.send("connected")

        # leave
        elif content == '-leave':
            if message.guild.voice_client is None:
                await message.channel.send("接続していません。")
                return

            # 切断する
            await message.guild.voice_client.disconnect()

        # stop
        elif content == '-stop':
            print("stop")
            message.guild.voice_client.stop()
            playController.stop()

        # next
        elif content == '-n':
            print("next")
            message.guild.voice_client.stop()

        # list
        elif content == '-list':
            print("list")
            await self.showList(message)

        # loop
        elif content == '-loop':
            print("loop")
            playController.loop(True)

        # post
        if len(contentList) >= 2 and (contentList[0] == '-r' or contentList[0] == '-remove'):
            if not contentList[1].isdigit():
                await message.channel.send("Please enter number")
                return
            num = int(contentList[1])
            if len(self.playList) < num or num <=0:
                await message.channel.send("out of range")
                return
            del self.playList[num-1]
            await message.channel.send("delete no." + str(num))

    async def on_voice_state_update(self,member, before, after):
        if member != client.user:
            return
        if after.channel is None:
            print("leave bot")
            playController.ini()

    # -p のコマンド受信時
    async def popCommand(self,message,arg):
        if message.guild.voice_client is None:
            # ボイスチャンネルに接続する
            await message.author.voice.channel.connect()
            await message.channel.send("接続しました。")

        # 先頭の'-p'を削除
        del arg[0]

        # 検索トップのアイテム
        firstItem = youtubeDataAPI.getTopSearchResults(arg)
        url= youtubeDataAPI.getURL(firstItem)
        title = firstItem["snippet"]["title"]
        thumbnails = firstItem["snippet"]["thumbnails"]["default"]["url"]

        musicData = MusicData(url,title,thumbnails)

        # embed の作成
        embed = discord.Embed(title="🦀 add music 🦀",description=title)
        embed.set_thumbnail(url=thumbnails)
        await message.channel.send(embed=embed)

        playController.addQueue(message,musicData)

    # -listのコマンド受信時
    async def showList(self,message):
        #　listに追加
        # embed の作成
        embed = discord.Embed(title="🦀 music list 🦀", color=0x00a895)
        for i, data in enumerate(playController.playList):
            play = "▶ " if i == playController.nowPlayCount else ""
            embed.add_field(name="no."+str(i+1), value= play + data.title, inline=False)
        await message.channel.send(embed=embed)

client = MyClient()
client.run(DIDCODE_TOKEN)