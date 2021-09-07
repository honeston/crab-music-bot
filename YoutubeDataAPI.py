from Config import *
import requests
import urllib

class YoutubeDataAPI():

    def getTopSearchResults(self,searchWord):
        queueMessage = self.cleateQuote(searchWord)

        # youtubeで検索！
        response = self.requestsYoutube(queueMessage)

        # 検索結果の有無チェック
        if len(response["items"]) < 1:
            return

        return response["items"][0]

    def getURL(self,item):
        return YOUTUBE_PLAY_URL.format(item["id"]["videoId"])

    # 検索用フォーマットの作成
    def cleateQuote(self,quoteList):
        quote=""
        for i, quoteMessage in enumerate(quoteList):
            quote += "+" + urllib.parse.quote(quoteMessage)
        
        return quote

    # youtubeで検索(return辞書型,json)
    def requestsYoutube(self,quote):
        responseData = requests.get(YOUTUBE_SURCH_URL.format(quote,YOUTUBE_API_KEY))
        print(quote)
        if responseData.status_code < 200 or responseData.status_code > 199:
            print("access error:")
            #ここにエラー処理TODO
        return responseData.json()

youtubeDataAPI = YoutubeDataAPI()