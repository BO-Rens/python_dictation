#!/usr/bin/env python3 
import pickle
import RPi.GPIO as GPIO
import time
import pyaudio
import wave
import pixel
import csv
import apa102
import time
from time import strftime, localtime
import threading
import datetime
try:
    import queue as Queue
except ImportError:
    import Queue as Queue

# start monitoring button press on GPIO pin 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


# initialise the arrays for colloring the leds
# arrays contain 9 elements :
# 0 - 2 = R - G  - B values of led1 / 3 - 5 : led2 / 
# the blinking switches between colors in array A eand array B
# setting them to thesame value enables solid color or off (= 0 - 0 - 0)
colorsA=[0, 0, 0, 0, 0, 0, 0, 0, 0]
colorsB=[0, 0, 0, 0, 0, 0, 0, 0, 0]

led=pixel.Pixels()
# led.wakeup()
time.sleep(2)
led.off()

recording = False
stoprecording = False
startrecording = False


# Create datetimestring for printing, logging and identifing recordings - format : YYYYMMDD.HHMMSS
def datetimestring():
	datetimestr=str(strftime("%Y%m%d.%H%M%S", localtime()))
	return datetimestr

# Function to detect button presses and set the global variables recording - stop / startrecording
def callback1(channel):
    print('Button pressed!')
    #time.sleep(1)
    global recording
    global stoprecording
    global startrecording
    if GPIO.input(17) == 1:
        if recording == True:
            recording = False
            print('button press request stop recording')
            stoprecording = True
            leds(0)

        else :
            recording = True
            print('button press request start recording')
            startrecording = True
            leds(1)

# Function to write log lines - appending the new line
def log(line):
    writeline = (str(datetime.datetime.now()) + ' : ' + line + ' \n')
    file = open('/home/pi/Python/dictation/logrecord.txt','a') 
    file.write(writeline)
    file.close() 

# Function to let the leds flash or be set with a static color
#
# patern is saved in a picle file


def leds(patern):
    led.off()
    #global colorsA
    #global colorsB
    rf=open('recfile' , 'wb')
    pickle.dump(patern,rf)
    rf.close()
    led.blinking()

#########################
##### MAIN PROGRAM ######
#########################

leds(2)

log('record script started')

# Initialise button detection
bounce = 100
GPIO.add_event_detect(17, GPIO.RISING, callback=callback1, bouncetime=bounce)


# Initialise parameter for recorder object 
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

print("starting program - " + datetimestring() + " - wait for button press")


# Program Loop

while True:
	if recording == True:
		if startrecording == True: 
			try:
				p = pyaudio.PyAudio()
				stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
				frames = []
				startrecording = False
				datetimestr=datetimestring()
				print("recording started : " + datetimestr)
			except:
				log('recording failed')
		data = stream.read(CHUNK)
		frames.append(data)

	else:
		if stoprecording == True:
			# Stop recording
			try:
				stream.stop_stream()
				stream.close()
				p.terminate()
				# Save the recorded stream as a .wav file
				wf = wave.open('/home/pi/Python/dictation/recordings/'+datetimestr+'.wav', 'wb')
				wf.setnchannels(CHANNELS)
				wf.setsampwidth(p.get_sample_size(FORMAT))
				wf.setframerate(RATE)
				wf.writeframes(b''.join(frames))
				wf.close()
				print("recording saved as : " +datetimestr+".wav")
				stoprecording = False
			except:
				log('failed to convert recording to wav')
				led()
			# Turn of the leds
			leds(0)
			# After recording the filename is added to the recordings list with status '1' : to be converted
			try : 
				
				with open('/home/pi/Python/dictation/recordings.txt','a') as recordings_list:
					recording_writer = csv.writer(recordings_list, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
					recording_writer.writerow([datetimestr, '1'])
				recordings_list.close()
			except:
				log('failed to add recording to csv file')
			print("recording complete - wait for button press")
		time.sleep(0.5)

