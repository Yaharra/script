# !python
import os
import os.path
from os import path
import smtplib
from smtplib import SMTPException
from email.message import EmailMessage
import logging
import datetime
from collections import Counter
import json

### VARIABLES ###

#Variable env. pour e-mail
mail = os.environ.get('GMAIL_USER')
password = os.environ.get('GMAIL_PSWD')

### INITIALISATION ###

logging.basicConfig(filename='logs.txt', level=logging.INFO, format='%(asctime)s -- %(levelname)s : %(message)s')

thisFolder = os.path.dirname(os.path.abspath(__file__))
myFile = os.path.join(thisFolder, r"config.json")

with open(myFile) as config_json:
    config = json.load(config_json)

### FONCTIONS ###

#récupération des fichiers
def getElement(path): 
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    print(files)        
    return files

#Création des dossier de tri (si non existant)
def createFolder(path):
    try:
        os.mkdir(path)
    except OSError as oe:
        print(str(oe))
    else:
        print("New folder created")

#Aquisition de l'extension des fichiers
def getExtension(path):
    filename, extension = os.path.splitext(path)
    return extension

#Déplacement des fichiers dans les dossiers de tri
def moveFile(file, path):
    originPath = config["Folder"]["folder"] +'\\'+file
    fullpath = path+'\\'+file
    
    if(os.path.exists):
        os.rename(originPath, fullpath)
    else:
        print("Folder does not exist")

#Vérification de l'existance des dossiers de tri
def verifyPath():
    for i in range(len(config["Extension"])):
        if(not(os.path.exists(config["Extension"][str(i)][0]))):
            createFolder(config["Extension"][str(i)][0])
    i+=1

#Envoi e-mail confirmation
def sendEmail(mail, password, message):

    msg = EmailMessage()
    msg['Subject'] = "Download Folder files sorting"
    msg['From'] = mail
    msg['To'] = mail
    msg.set_content(message)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(mail, password)
        server.send_message(msg)
        server.quit()
        logging.info('Mail Sent')
    except Exception as e:
        print(str(e))
        logging.exception('Error while sending e-mail.')

#Contenu du message de l'e-mail
def messageEmail(iteration, fileMoved, fileNotMoved):
    zeroSorted = "No file were needed to be sorted in the download folder."
    oneSorted = "The download folder has been cleared.\n"+str(iteration)+" file was successfully sorted."
    severalSorted = "The download folder has been cleared.\n"+str(iteration)+" files were successfully sorted."

    if(iteration == 0):
        message = zeroSorted
    elif(iteration==1):
        message = oneSorted
        for file in fileMoved:
            message += "\n- "+file
    else:
        message = severalSorted
        for file in fileMoved:
            message += "\n- "+file

    if(len(fileNotMoved)!=0):
        message += "\n\n The following files were not sorted :"
        for file in fileNotMoved:
            message += "\n- "+file

    #logging.info(message)

    return message


### MAIN ###

def main():
    files = getElement(config["Folder"]["folder"])
    verifyPath()
    iteration = 0
    fileMoved = []

    for file in files:
        extension = getExtension(file)
        for i in range(len(config["Extension"])):
            for extensions in config["Extension"][str(i)][1]:
                if(extension == extensions):
                    moveFile(file, config["Extension"][str(i)][0])
                    iteration+=1
                    fileMoved.append(file)
        i+=1

    
    fileNotMoved = list((Counter(files) - Counter(fileMoved)).elements())
    message = messageEmail(iteration, fileMoved, fileNotMoved)
    sendEmail(mail, password, message)

main()