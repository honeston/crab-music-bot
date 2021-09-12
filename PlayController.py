
import discord
import pafy
from threading import Timer

class PlayController:
    playList = []
    isPlaydQueue = False
    nextPlayCount = 0
    nowPlayCount = 0
    isLoop = False
    timer = None

    def ini(self):
        self.isPlaydQueue = False
        self.nextPlayCount = 0
        self.nowPlayCount = 0
        self.isLoop = False
        self.playList.clear()
        if self.timer is not None:
           self.timer.cancel()
        self.timer = None


    def play(self,message):
        self.playing(message)
    
    def next(self,message):
        message.guild.voice_client.stop()
        self.playing(message)

    def stop(self,message):
        print("stop")
        if self.timer is not None:
           self.timer.cancel()
        message.guild.voice_client.stop()
        #self.ini()

    def loop(self,isLoop):
        print("loop")
        self.isLoop = isLoop

    def remove(self,num):
        print("remove")
        if not num.isdigit():
            return -1
        num = int(num)
        if len(self.playList) < num or num <=0:
            return -2
        del self.playList[num-1]

    # 再生監視とキューの取り出し、TODO
    def playing(self,message):
        if (not message.guild.voice_client.is_playing()):
            if self.isLoop and self.nextPlayCount >= len(self.playList):
                self.nextPlayCount = 0
            if (self.nextPlayCount < len(self.playList)):
                self.nowPlayCount = self.nextPlayCount
                url = self.playList[self.nextPlayCount]['url']
                video= pafy.new(url)
                best= video.getbestaudio()
                print(video.length)
                print(video.duration)
                self.nextPlayCount+=1
                message.guild.voice_client.play(discord.FFmpegPCMAudio(best.url))
                self.timer = Timer(video.length, self.playing, (message, ))
                self.timer.start()
    
    # キューの追加
    def addQueue(self, message ,data):
        #　listに追加
        self.playList.append(data)
        self.play(message)
            
playController = PlayController()