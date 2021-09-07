
import discord
import pafy
from threading import Timer

class PlayController:
    playList = []
    isPlaydQueue = False
    nextPlayCount = 0
    nowPlayCount = 0
    isLoop = False

    def ini(self):
        self.isPlaydQueue = False
        self.nextPlayCount = 0
        self.nowPlayCount = 0
        self.isLoop = False
        self.playList.clear()

    def stop(self):
        print("stop")
        self.ini()

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
    def playQueue(self,message):
        if (self.isPlaydQueue):
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
                    timer = Timer(3, self.playQueue, (message, ))
                    timer.start()
                else:
                    self.isPlaydQueue = False
            else:
                timer = Timer(3, self.playQueue, (message, ))
                timer.start()
    
    # キューの追加
    def addQueue(self, message ,data):
        #　listに追加
        self.playList.append(data)
        if not self.isPlaydQueue:
            self.isPlaydQueue = True
            self.playQueue(message)

playController = PlayController()