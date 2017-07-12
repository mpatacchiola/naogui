# coding=utf-8

#The coding line above it is necessary in order to
#deal with some Slovak characters. Python will default 
#to ASCII as standard encoding if no other encoding 
#hints are given.


import urllib

#Voice: Dagmar4
#Sentence: "Bratislava je pekn mesto."
#http://speech.savba.sk/cgi-bin/patronus/tts/patronus_sk_tts3.py?voice=hmm_bajnokova_20160607&text=Bratislava+je+pekn%C3%A9+mesto.&rate=0&pitch=0&volume=0&rate_n=0&pitch_n=0&volume_n=0&mode=adapt


#Text to Speech
sentence = "trvalý pobyt mám v okrese Senec"
params = urllib.urlencode({'voice': 'hmm_bajnokova_20160607', 'text': sentence,  'rate': 0, 'pitch': 0, 'volume': 0, 'rate_n': 0, 'pitch_n': 0, 'volume_n': 0, 'mode': 'adapt' })
print(params)
service_url = 'http://speech.savba.sk/cgi-bin/patronus/tts/patronus_sk_tts3.py'
urllib.urlretrieve(service_url, './file.wav', data=params)




