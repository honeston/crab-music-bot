import discord
import logging
import yaml
import pafy
import requests
import queue
from threading import Timer
import urllib.parse

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with open('product.yaml', 'r') as yml:
    config = yaml.load(yml)

class MyClient(discord.Client):
    playList = []
    isPlaydQueue = False
    nextPlayCount = 0
    nowPlayCount = 0
    isLoop = False
    
    # コンストラクタ
    def __init__(self, youtubeAPIkey):
        super().__init__()
        self.youtubeAPIkey = youtubeAPIkey

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
            self.ini()

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
            self.loopList(True)


    async def on_voice_state_update(self,member, before, after):
        print("leave")
        if member != client.user:
            return
        if after.channel is None:
            print("leave bot")
            self.ini()
  

    def ini(self):
        self.isPlaydQueue = False
        self.nextPlayCount = 0
        self.nowPlayCount = 0
        self.isLoop = False
        self.playList.clear()


    # -p のコマンド受信時
    async def popCommand(self,message,arg):
        if message.guild.voice_client is None:
            # ボイスチャンネルに接続する
            await message.author.voice.channel.connect()
            await message.channel.send("接続しました。")

        # 先頭の'-p'を削除
        del arg[0]
        queueMessage = self.cleateQuote(arg)

        # youtubeで検索！
        response = self.requestsYoutube(queueMessage,self.youtubeAPIkey)


        # 検索結果の有無チェック
        if len(response["items"]) < 1:
            await message.channel.send("not hit")
            return

        # 検索トップのアイテム
        firstItem = response["items"][0]
        url= "https://www.youtube.com/watch?v="+ firstItem["id"]["videoId"]
        title = firstItem["snippet"]["title"]
        thumbnails = firstItem["snippet"]["thumbnails"]["default"]["url"]

        musicData = MusicData(url,title,thumbnails)

        # embed の作成
        embed = discord.Embed(title="🦀 add music 🦀",description=title)
        embed.set_thumbnail(url=thumbnails)
        await message.channel.send(embed=embed)

        self.addQueue(message,musicData)

    # -listのコマンド受信時
    async def showList(self,message):
        #　listに追加
        # embed の作成
        embed = discord.Embed(title="🦀 music list 🦀", color=0x00a895)
        for i, data in enumerate(self.playList):
            play = "▶ " if i == self.nowPlayCount else ""
            embed.add_field(name="no."+str(i+1), value= play + data.title, inline=False)
        await message.channel.send(embed=embed)
        print(self.nextPlayCount)
        print(len(self.playList))

    # -listのコマンド受信時
    def loopList(self,isLoop):
        self.isLoop = isLoop


    # 検索用フォーマットの作成
    def cleateQuote(self,quoteList):
        quote=""
        for i, quoteMessage in enumerate(quoteList):
            quote += "+" + urllib.parse.quote(quoteMessage)
        
        return quote

    # youtubeで検索(return辞書型,json)
    def requestsYoutube(self,quote,APIkey):
        responseData = requests.get('https://www.googleapis.com/youtube/v3/search?type=video&part=snippet&q='+quote+'&key='+APIkey)
        print(quote)
        if responseData.status_code < 200 or responseData.status_code > 199:
            print("access error:")
            #ここにエラー処理TODO
        return responseData.json()

    # キューの追加
    def addQueue(self, message ,data):
        #　listに追加
        self.playList.append(data)
        if not self.isPlaydQueue:
            self.isPlaydQueue = True
            self.playQueue(message)
        

    # 再生監視とキューの取り出し、TODO
    def playQueue(self,message):
        if (self.isPlaydQueue):
            if (not message.guild.voice_client.is_playing()):
                if self.isLoop and self.nextPlayCount >= len(self.playList):
                    self.nextPlayCount = 0
                if (self.nextPlayCount < len(self.playList)):
                    self.nowPlayCount = self.nextPlayCount
                    url = self.playList[self.nextPlayCount].url
                    video= pafy.new(url)
                    best= video.getbestaudio()
                    print(video.length)
                    print(video.duration)
                    self.nextPlayCount+=1
                    message.guild.voice_client.play(discord.FFmpegPCMAudio(best.url))
                    timer = Timer(3, self.playQueue, (message, ))
                    timer.start()
                else:
                    self.isPlaydQueue = False
            else:
                timer = Timer(3, self.playQueue, (message, ))
                timer.start()

class MusicData:
    def __init__(self, url=None,title=None,thumbnails=None):
        self.url = url
        self.title = title
        self.thumbnails = thumbnails

client = MyClient(config['apikey']['youtube'])
client.run(config['apikey']['discord'])