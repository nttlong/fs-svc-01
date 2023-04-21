import datetime

from  cyx.media.video import VideoServices
import cy_kit
import cy_docs
data=dict(
    a=datetime.datetime.utcnow()
)
fx=  cy_docs.to_json_convertable(data)
print(fx)
sv = cy_kit.singleton(VideoServices)
import speech_recognition as sr
ret=sv.get_audio(f"/home/vmadmin/python/v6/file-service-02/temp-data/ok.mp4")
AUDIO_FILE = ret



r = sr.Recognizer()
with sr.AudioFile(AUDIO_FILE) as source:
    audio = r.record(source)  # read the entire audio file
    txt = r.recognize_sphinx(audio,language="vi-VI")
    print(txt)
# import pyttsx3
# engine = pyttsx3.init()
# engine.say("I will speak this text")
# engine.runAndWait()
# import speech_recognition as sr
# import pyaudio
# r = sr.Recognizer()
# with sr.AudioSource() as source:
# print("Mời bạn nói: ")
# audio = r.listen(source)
# try:
# text = r.recognize_google(audio,language="vi-VI")
# print("Bạn -->: {}".format(text))
# except:
# print("Xin lỗi! tôi không nhận được voice!")
# print(ret)