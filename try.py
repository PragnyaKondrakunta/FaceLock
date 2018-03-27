import requests
#!/usr/bin/env python
import os, sys
import RPi.GPIO as GPIO
from time import sleep
import json
import subprocess
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from cloudinary.api import delete_resources_by_tag, resources_by_tag

# config
os.chdir(os.path.join(os.path.dirname(sys.argv[0]), '.'))
if os.path.exists('settings.py'):
    exec(open('settings.py').read())

DEFAULT_TAG = "python_sample_basic"

def dump_response(response):
    print("Upload response:")
    for key in sorted(response.keys()):
        print("  %s: %s" % (key, response[key]))

def upload_files(id1):
    print("--- Upload a local file")
    response = upload("image.jpg", tags = DEFAULT_TAG)
    dump_response(response)
    url, options = cloudinary_url(response['public_id'],
        format = response['format'],
        width = 200,
        height = 150,
        crop = "fill"
    )
    print(url)
    id2 = detect_faces(url)
    verify_faces(id1,id2)


def verify_faces(id1,id2):
    headers = { 'Ocp-Apim-Subscription-Key' : 'f4601f44831c40c892488f17436dd5cc' }
    face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/verify'
    response= requests.post(face_api_url,headers=headers,json={'faceId1':id1,'faceId2':id2})
    res=response.json()
    if(res['isIdentical']==True):
	open_door()
    else:
	subprocess.Popen(['omxplayer','-o','local','deny.mp3']).wait()
	
	
def open_door():
	print('opening door')
	subprocess.Popen(['omxplayer','-o','local','welcome.mp3']).wait()
	setangle(180)
	pwm.stop()
	GPIO.cleanup()


def detect_faces(url):
    headers = { 'Ocp-Apim-Subscription-Key' : 'f4601f44831c40c892488f17436dd5cc' }

    params = {
            'returnFaceId':'true',
            'returnFaceLandmarks':'false',
            'returnFaceAttributes':'age,gender',
    }
    face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
    image_url = url
    response= requests.post(face_api_url,params=params,headers=headers,json={'url':image_url})
    faces=response.json()
    print('detected face count:'+str(len(faces)))
    if(len(faces)>0):
	id=faces[0]['faceId']
        return(id)
    else:
	print('no face found')
	return('no id')


def takepic(id1):
	os.system('fswebcam -S 8 image.jpg')
	upload_files(id1)

def setangle(angle):
        duty = angle/18 +2
        GPIO.output(03,True)
        pwm.ChangeDutyCycle(duty)
        sleep(0.1)
        GPIO.output(03,False)
        pwm.ChangeDutyCycle(0)


GPIO.setmode(GPIO.BCM)
GPIO.setup(3,GPIO.OUT)
url1 = 'http://res.cloudinary.com/kmit/image/upload/v1522077495/o6blldyfv2w26jh8rb9z.jpg'
id1=detect_faces(url1)
pwm = GPIO.PWM(03,50)
pwm.start(0)
takepic(id1)
