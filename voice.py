from gtts import gTTS
import subprocess
tts=gTTS(text='Unable to identify Person. Access denied',lang='hi')
tts.save("deny.mp3")
subprocess.Popen(['omxplayer','-o','local','deny.mp3']).wait()