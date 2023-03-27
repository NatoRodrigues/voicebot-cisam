import time
import requests
import speech_recognition as sr     # import the library
from gtts import gTTS
from playsound import playsound
'''
Engine de voz pyttsx3
engine = pyttsx3.init()
engine.say(mensagem)
engine.runAndWait()
 '''
bot_message =  ""

message=""
loop = 1
 
while loop == 1:
    r = sr.Recognizer()  # initialize recognizer
    with sr.Microphone(device_index=1) as source:  # mention source it will be either Microphone or audio files.
        print("Fale alguma coisa :")
        audio = r.listen(source)  # listen to the source
        try:
            message = r.recognize_google(audio, language="pt-BR")  # use recognizer to convert our audio into text part.
            print("Você disse : {}".format(message))

        except:
            print("Desculpe, náo reconheci sua voz")
    if len(message)==0:
        continue
    r = requests.post('http://localhost:5007/webhooks/rest/webhook', json={"message": message})

    print("Bot disse: ",end=' ')
    for i in r.json():
        bot_message = i['text']
        myobj = gTTS(text=bot_message, lang='pt-BR')
        myobj.save("msg.mp3")
        time.sleep(1)
        playsound('msg.mp3')


# mytext = 'Olá, eu sou a assistente do cisam,se quiser posso te auxiliar, caso queira é só falar "Olá"!'        
# language = 'pt-BR'
# myobj = gTTS(text=mytext, lang='pt-BR')
# time.sleep(1)
# myobj.save("welcome.mp3")

# print('salvo')
# subprocess.call(['mpg321', "welcome.mp3", '--play-and-exit'])



# # myobj = gTTS(text=bot_message)
# # myobj.save("welcome.mp3")
# # print('saved')
# # # Playing the converted file
# # subprocess.call(['mpg321', "welcome.mp3", '--play-and-exit'])

# while bot_message != "Bye" or bot_message!='tchau':

#     r = sr.Recognizer()  # initialize recognizer
#     with sr.Microphone(device_index=0) as source:  # mention source it will be either Microphone or audio files.
#         print("Fale alguma coisa :")
#         audio = r.listen(source)  # listen to the source
#         try:
#             message = r.recognize_google(audio, language="pt-BR")  # use recognizer to convert our audio into text part.
#             print("Você disse : {}".format(message))

#         except:
#             print("Desculpe, náo reconheci sua voz")
#     if len(message)==0:
#         continue
#     print("Enviando mensagem...")

#     r = requests.post('http://localhost:5007', json={"message": message})

#     print("Bot disse, ",end=' ')
#     for i in r.json():
#         bot_message = i['text']
#         print(f"{bot_message}")

#     myobj = gTTS(text=bot_message, lang='pt-BR')
#     myobj.save("welcome.mp3")
#     print('saved')
#     # toca o arquivo convertido
#     subprocess.call(['mpg321', "welcome.mp3", '--play-and-exit'])
