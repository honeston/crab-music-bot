import requests
import json
from Config import *


def createVoice(text):
    responseData = requests.post(SPEAK_QUERY_URL.format(text))
    responseJson = responseData.json()
    responseJson['volumeScale'] = 2
    headers = {'Content-Type': 'application/json'}
    urlData = requests.post(url = SPEAK_VOICE_URL,data=json.dumps(responseJson), headers=headers).content
    filename='audio.wav'
    with open(filename ,mode='wb') as f:
        f.write(urlData)
    return 'audio.wav'