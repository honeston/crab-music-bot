import discord
from Config import *
from PlayController import playController
from YoutubeDataAPI import youtubeDataAPI

class DiscordClient(discord.Client):

    commandList = {"post":["-post","-p"],\
                    "join":["-join","-j"],\
                    "leave":["-leave"],\
                    "stop":["-stop","-s"],\
                    "list":["-list"],\
                    "next":["-next","-n"],\
                    "remove":["-remove","-r"],\
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
        if len(contentList) >= 2 and (inputCommand in self.commandList['post']):
            await self.popCommand(message,contentList)

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
            message.guild.voice_client.stop()
            playController.stop()

        # next
        elif inputCommand in self.commandList['next']:
            print("next")
            message.guild.voice_client.stop()

        # list
        elif inputCommand in self.commandList['list']:
            print("list")
            await self.showList(message)

        # loop
        elif inputCommand in self.commandList['loop']:
            print("loop")
            playController.loop(True)

        # remove
        elif len(contentList) >= 2 and (inputCommand in self.commandList['remove']):
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
        embed = discord.Embed(title="🦀 music list 🦀", color=0x00a895)
        for i, data in enumerate(playController.playList):
            play = "▶ " if i == playController.nowPlayCount else ""
            embed.add_field(name="no."+str(i+1), value= play + data['title'], inline=False)
        await message.channel.send(embed=embed)