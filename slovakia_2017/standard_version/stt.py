# coding=utf-8

#The coding line above it is necessary in order to
#deal with some Slovak characters. Python will default 
#to ASCII as standard encoding if no other encoding 
#hints are given.

import requests
from xml.dom import minidom
import os

'''
<html>

<h1>Demo ASR</h1><br>
<form method="post" action="/cgi-bin/patronus/asr/patronus_sk_asr3.py" enctype="multipart/form-data">
Audio: <input type="file" name="audio" /><br>
<input type="radio" name="gender" value=male checked>male<br>
<input type="radio" name="gender" value=female>female<br>
<input type="submit" value="GO" />
</form>

</html>
'''

'''
<ASR>
<text>trvalý pobyt mám v okrese Senec</text>
<sr_phone_s>9.981516</sr_phone_s>
<sr_syllable_s>4.172486</sr_syllable_s>
<sr_syllable_s_orig>4.066544</sr_syllable_s_orig>
<sr_word_s>1.478743</sr_word_s>
<speech_duration_s>2.705000</speech_duration_s>
<hesitation_duration_s>0.215000</hesitation_duration_s>
<speech_syllable_count>11</speech_syllable_count>
<speech_word_count>4</speech_word_count>
<speech_phone_count>27</speech_phone_count>
<speech_start_point>0.175000</speech_start_point>
<speech_end_point>3.035000</speech_end_point>
<config>patronus_male.cfg</config>
<sr_syllable_s_praat>4.3</sr_syllable_s_praat>
<sr_speakingrate_praat>3.491</sr_speakingrate_praat>
<F0_Mean>102.1</F0_Mean>
<F0_Sigma>7.65</F0_Sigma>
<INT_Mean>59.984446023037556</INT_Mean>
<INT_Max>71.16576961254609</INT_Max>
<INT_Min>20.706640215428475</INT_Min>
<SR_Mean>4.236243</SR_Mean>
<time>2.91015911102</time>
</ASR>
'''

#The name of the input field is 'audio' and it must be used to send the request
upload_url = 'http://speech.savba.sk/cgi-bin/patronus/asr/patronus_sk_asr3.py'
data = {'audio': ('audio.wav', open('audio.wav', 'rb'))}
xml = requests.post(upload_url, files=data)
print (xml.text)


#ATTENTION: the 'encode' method must be used for each string
#otherwise some Slovak character can arise an exception
xml_parsed = minidom.parseString(xml.text.encode('utf-8').strip())
#Read some fields of the xml file
returned = xml_parsed.getElementsByTagName("text")[0]
print("text ........ %s" %returned.firstChild.data)
returned = xml_parsed.getElementsByTagName("time")[0]
print("time ........ %s" %returned.firstChild.data)
returned = xml_parsed.getElementsByTagName("speech_word_count")[0]
print("word count ........ %s" %returned.firstChild.data)
