
#!/usr/bin/env python
# encoding: utf-8

# General dependencies
import time
import datetime

# Mailer dependencies
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

# Speech recognition dependencies
import speech_recognition as sr # pip3 install SpeechRecognition

# Connection status dependencies
import urllib.request

# CS reading dependencies
import csv

# led blinking dependencies
import pickle

# Configparser to store password outside of code
import configparser

#################
### FUNCTIONS ###
#################


# Function to send presented string 'bodytext' as the email body
#
# https://gist.github.com/rdempsey/22afd43f8d777b78ef22 
# Thanks Robert 
# python_3_email_with_attachment.py - Created by Robert Dempsey on 12/6/14. - Copyright (c) 2014 Robert Dempsey. 
def sendmail(bodytext,subject):
	COMMASPACE = ', '
	# read the sender, recipient and email password from file
	config = configparser.ConfigParser()
	config.read("/home/pi/credentials.txt")
	password = config.get("mail","passwd")
	to = config.get("mail","recipient")
	sendr = config.get("mail","sender")
	log(sendr)
	log(to)
	log(password)

	# Create the enclosing (outer) message
	outer = MIMEMultipart()
	outer['Subject'] = str(subject) ###       =>       TO BE DEBUGGED - NO SUBJECT IN MAIL !!!
	outer['To'] = COMMASPACE.join(to)
	outer['From'] = sendr
	outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

	try:
		with smtplib.SMTP('smtp.gmail.com', 587) as s:
			s.ehlo()
			s.starttls()
			s.ehlo()
			s.login(sendr, password)
			s.sendmail(sendr, to, bodytext)
			s.close()
		print("Email sent!")
	except:
		log('unable to send email')

# Function for audio analysis of the presented .wav file
#
# the loc   tion of the .wav file is passed to the function as a string
# tutorial from https://realpython.com/python-speech-recognition/
# Resolved issues :
#    - Error thrown in line 'r.recognize_google(audio)' resolved by installing FLAC support
#          -> sudo apt-get install flac
# Setting to dutch : https://www.tropo.com/docs/scripting/international-features/multilingual-speech-recognition
def speechrecognition(filelocationstring):
    global analysiserror
    leds(2)
    r = sr.Recognizer()
    recording = sr.AudioFile(filelocationstring) 
    with recording as source:
        audio = r.record(source)

    try:
    	returnstr=r.recognize_google(audio, language="nl-BE") # We don't speak "nl-nl" and we don't drink heineken!
    except BrokenPipeError:
        returnstr = 'BrokenPipeError'
        analysiserror = 2
        print ('analysis failed : ')
    except:
        returnstr = 'General exception'
        analysiserror = 1
        print ('analysis failed : ')
    else:
        print('analysis sucessfull : ')
        analysiserror = 0
    finally:
        if analysiserror > 0 :
        	log('analysiserror : ' +  str(analysiserror) + ' - ' + returnstr)
        return returnstr

# Function to determine if the system is connected to the internet for analysis
# https://stackoverflow.com/questions/1949318/checking-if-a-website-is-up-via-python
#
def online():
    try:
        if urllib.request.urlopen("https://www.google.be").getcode() == 200:
            status = True
            leds(1)
        else:
            status = False
            leds(0)
    except:
        status == False
        log('failed to check connectivity')
    return status

# Function to let the leds flash or be set with a static color
#
# code corresponding to the led is saved to a picle file for use in a paralel process
def leds(patern):
	fa = open('anafile', 'wb')
	pickle.dump(patern, fa)
	fa.close()

# Function to write back to the CSV file
# Writes the Array containing the recordings and status back to the CSV file
# csv.DictWriter was chosen over writer to keep the correct order of the fields
# The cvs.writer would randomly inverse the order of the variables
# https://docs.python.org/3/library/csv.html
def update_csv(recording_array):
	try: 
		recordings_list = open('/home/pi/Python/dictation/recordings.txt','w', newline='')
		fn =  ['Recording', 'Status']
		recording_writer = csv.DictWriter(recordings_list, fieldnames=fn, dialect='excel', delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		#recording_writer.writeheader()
		i = 0
		while i < len(recording_array):
			#print ('writing line : ' + str(recording_array[i][0]) + " - " + str(recording_array[i][1]))
			recording_writer.writerow({'Recording': recording_array[i][0], 'Status' : recording_array[i][1]})
			i+=1
		recordings_list.close()
		print('list updated')
	except:
		log('failed to write CSV')

# Function to read from the CSV file.  
# The content of CSV is returned as array
def read_csv():
	try : 
	    recordings_list = open('/home/pi/Python/dictation/recordings.txt','r')
	    recording_reader = csv.reader(recordings_list, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	    csv_array=[]
	    for row in recording_reader:
	        csv_array.append(row)
	    recordings_list.close()
	    return csv_array
	    print('list read')
	except:
		log('failed to read CSV')

# Function to write log lines - appending the new line
def log(line):
    writeline = (str(datetime.datetime.now()) + ' : ' + line + ' \n')
    file = open('/home/pi/Python/dictation/loganalyse.txt','a') 
    file.write(writeline)
    file.close() 


#################### 
### MAIN PROGRAM ### 
####################

leds(1)
# led.wakeup()
time.sleep(2)


analysiserror = 0
directorystring = str('/home/pi/Python/dictation/recordings/')
returnstring = str(' ')


log('analyse script started - online = ' + str(online()))
while True:
	if online() == True:
		recordings_array=read_csv()
		
		i=0
		while i < len(recordings_array):
			#print ('recordings_array[i][1] : ' + recordings_array[i][1])
			if str(recordings_array[i][1])=='1': 
				returnstring=speechrecognition(directorystring + str(recordings_array[i][0]) + '.wav')
				if analysiserror == 0:
					sendmail(returnstring,str(recordings_array[i][0]))
					recordings_array[i][1]='0'

				else:
					recordings_array[i][1]='2'
					analysiserror=0
				# update and reload the CSV file
				# (in case an new recording was made during ongoing analysis) 
				update_csv(recordings_array)
				recordings_array=read_csv()
				#print('line ==1')
			print('array item : '+ str(i) + ' recording : ' + recordings_array[i][0] + ' - ' + recordings_array[i][1])
			i+=1
	timer = 5
	while timer > 0:
		print (str(timer))
		time.sleep(1)
		timer -= 1
	


################################
# TO DO (in order of priority)
# - Start recording without button press upon reboot - solved 
# - mail subject not set
################################