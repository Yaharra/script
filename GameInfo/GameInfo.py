#! python
import requests
import json
import os
import sys
import smtplib
import logging
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

### INITIALIZATION ###

#logging
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s -- %(levelname)s : %(message)s')

#json
thisFolder = os.path.dirname(os.path.abspath(__file__))
myFile = os.path.join(thisFolder, r"ConfigGameInfo.json")

with open(myFile) as config_json:
    config = json.load(config_json)

#variables
emailAdress = os.environ.get('GMAIL_USER')
emailPassword = os.environ.get('GMAIL_PSWD')

### FUNCTIONS ###

#Get game identification from website API
def getGameId(gameList):
    gameId = []
    for i in range(1, len(gameList)):
        paylods = {"search":gameList[i]}
        r = requests.get(config['Games']['endpoint'], params=paylods)
        data = json.loads(r.text)['results']
        
        for j in range(20):
            if(gameList[i].upper() in data[j]['name'].upper()):
                gameId.append(data[j]['id'])
    
    return gameId

#Get game details with the game ID
def getGameInfo(gameId):
    gameInfo = []
    for i in range(len(gameId)):
        r = requests.get(config['Games']['endpoint']+"/"+str(gameId[i]))
        data = json.loads(r.text)
        name = data['name']
        released = data['released']
        rating = data['rating']
        img = data['background_image']
        description = data['description']
        temp = [name, released, rating, img, description]
        gameInfo.append(temp)

    return gameInfo

#Format the emailing message from the game information obtained
def formatMessage(gameInfo):
    message = ""
    for i in range(len(gameInfo)):
        message += "<h1>"+str(gameInfo[i][0])+"</h1>"
        message +="<div><i>Releasing date : "+str(gameInfo[i][1])+" / Rating : "+str(gameInfo[i][2])+"</i></div>"
        message +="<div><img src = \""+str(gameInfo[i][3])+"\" width = 500px height = 300px></div>"
        message +="<div>"+str(gameInfo[i][4])+"</div>"
        message +="<HR size=2 align=center width=500px>"
    
    msg = MIMEText(message, 'html', 'utf-8')

    return msg

#Sending the email
def sendEmail(message):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Game News"
    msg['From'] = emailAdress
    msg['To'] = emailAdress
    msg.attach(message)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(emailAdress, emailPassword)
            smtp.sendmail(emailAdress, emailAdress, msg.as_string())
            logging.info('Email successfully sent.')
    except Exception:
        logging.exception('Email could not be sent.')
    
        
                
def main():
    gameId = getGameId(sys.argv)
    gameInfo = getGameInfo(gameId)
    message = formatMessage(gameInfo)
    sendEmail(message)

main()