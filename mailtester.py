# General dependencies
import time
import datetime
import configparser

# Mailer dependencies
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


def sendmail(bodytext,subject):
	COMMASPACE = ', '
	# read the sender, recipient and email password from file
	config = configparser.ConfigParser()
	config.read("/home/pi/credentials.txt")
	password = config.get("mail","passwd")
	to = config.get("mail","recipient")
	sendr = config.get("mail","sender")
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
		print('unable to send email')

while True:
	bodytext = input("body text to send? : ")
	subject = input("subject? : ")
	sendmail(bodytext,subject)


	timer = 3
	while timer > 0:
		print (str(timer))
		time.sleep(1)
		timer -= 1