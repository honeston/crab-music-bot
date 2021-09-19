import discord
from Config import *
from PlayController import playController
from YoutubeDataAPI import youtubeDataAPI
from DataIO import save,load
from Speak import createVoice

class DiscordClient(discord.Client):

    commandList = {"post":["-post","-p"],\
                    "play":["-play"],\
                    "join":["-join","-j"],\
                    "leave":["-leave"],\
                    "stop":["-stop","-s"],\
                    "list":["-list"],\
                    "next":["-next","-n"],\
                    "remove":["-remove","-r"],\
                    "save":["-save"],\
                    "load":["-load"],\
                    "speak":["-speak","-sp"],\
                    "loop":["-loop"]}

    # 準備完了
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
    
    # メッセージ受信
    async def on_message(self, message):
        if message.author == self.user:
            return

        content = message.content
        contentList = content.split(' ')
        inputCommand = contentList[0]
        commandcheck = False
        for comands in self.commandList.values():
            for comand in comands:
                if inputCommand == comand:
                    commandcheck = True

        if not commandcheck:
            return
            
        if message.author.voice is None:
            await message.channel.send("You are not connected to a voice channel.")
            return

        if message.guild.voice_client is None:
            # ボイスチャンネルに接続する
            await message.author.voice.channel.connect()
            await message.channel.send("connected")

        print('Message from {0.author}: {0.content}'.format(message))

        # post
        if inputCommand in self.commandList['post']:
            if len(contentList) >= 2:
                await self.popCommand(message,contentList)
        # play
        elif inputCommand in self.commandList['play']:
            playController.play(message)

        # join
        elif inputCommand in self.commandList['join']:
            print("join")

        # leave
        elif inputCommand in self.commandList['leave']:
            if message.guild.voice_client is None:
                await message.channel.send("接続していません。")
                return
            # 切断する
            await message.guild.voice_client.disconnect()

        # stop
        elif inputCommand in self.commandList['stop']:
            print("stop")
            playController.stop(message)

        # next
        elif inputCommand in self.commandList['next']:
            print("next")
            playController.next(message)

        # list
        elif inputCommand in self.commandList['list']:
            print("list")
            await self.showList(message)

        # save
        elif inputCommand in self.commandList['save']:
            print("save")
            if len(contentList) >= 2:
                save(playController.playList,contentList[1])
            else:
                save(playController.playList)

        # load
        elif inputCommand in self.commandList['load']:
            print("load")
            playController.ini()
            if len(contentList) >= 2:
                playController.playList = load(contentList[1])
            else:
                playController.playList = load()

            playController.next(message)

        # loop
        elif inputCommand in self.commandList['loop']:
            print("loop")
            playController.loop(True)
        
        # speak
        elif inputCommand in self.commandList['speak']:
            print("speak")
            # https://github.com/Hiroshiba/voicevox_engine
            if SPEAK_ISAVAILABLE:
                filename = createVoice(contentList[1])
                message.guild.voice_client.play(discord.FFmpegPCMAudio(filename))

        # remove
        elif inputCommand in self.commandList['remove']:
            if len(contentList) >= 2:
                err = playController.remove(contentList[1])
                if err == -1:
                    await message.channel.send("Please enter number")
                if err == -2:
                    await message.channel.send("out of range")
                await message.channel.send("delete no." + contentList[1])

    async def on_voice_state_update(self,member, before, after):
        if member != self.user:
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

        musicData = {'url':url,'title':title,'thumbnails':thumbnails}

        # embed の作成
        embed = discord.Embed(title="🦀 add music 🦀",description=title)
        embed.set_thumbnail(url=thumbnails)
        await message.channel.send(embed=embed)

        playController.addQueue(message,musicData)

    # -listのコマンド受信時
    async def showList(self,message):
        #　listに追加
        # embed の作成
        tilte = "🦀 music list {0}🦀".format("🔁" if playController.isLoop else "")
        embed = discord.Embed(title=tilte, color=0x00a895)
        for i, data in enumerate(playController.playList):
            play = "▶ " if i == playController.nowPlayCount else ""
            embed.add_field(name="no."+str(i+1), value= play + data['title'], inline=False)
        await message.channel.send(embed=embed)