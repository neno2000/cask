# import re
import configparser
import tkinter as tk
from tkinter import *
import os
import filecmp
from xml.etree import ElementTree
import csv
import hashlib
import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib



class Feedback(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()


    def createWidgets(self):
        var = StringVar()
        self.hi_there = tk.Button(self)
        self.labl = tk.Label(self, textvariable=var, relief=RAISED)
        var.set("The test passed; all the ALA files are OK")
        self.labl.pack(side="top")
        self.QUIT = tk.Button(self, text="QUIT", fg="red",
                              command=root.destroy)
        self.QUIT.pack(side="bottom")


class Feedback2(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        var = StringVar()
        self.hi_there = tk.Button(self)
        self.labl = tk.Label(self, textvariable=var, relief=RAISED)
        var.set("The test did not passed, check the error report")
        self.labl.pack(side="top")
        self.QUIT = tk.Button(self, text="QUIT", fg="red",
                              command=root.destroy)
        self.QUIT.pack(side="bottom")


def copySingleMessages(iFile, iTmpFolder):
    file2Check = []
    # get the content in the files and save on temporary
    pass
    with open(iFile, 'rt', encoding='utf-8') as f:
        tree = ElementTree.parse(f)
        for node in tree.findall('.//Colleague'):  #
            timeSt = node.find('.//LastModifiedDateTime')
            collId = node.find('.//GlobalColleagueId')

            bType = node.find('.//TriggerTypeCode')
            if (bType.text == "ColleagueSaved"):
                batchType = "batch1"
            else:
                batchType = "batch2"
            suffix = timeSt.text + "_" + collId.text + "_" + batchType
            suffix = suffix.replace(":", "_")
            suffix = suffix.replace(".", "_")
            newFile = iTmpFolder + "\\" + suffix
            newFile = newFile + ".xml"
            file2Check.append(newFile)
            tree2 = ElementTree.ElementTree(element=None, file=None)
            tree2._setroot(node)
            ##anonymaze the data
            fName = tree2.find('.//FirstName')
            lName = tree2.find('.//LastName')
            email = tree2.find('.//EmailAddress')
            phone = tree2.find('.//PhoneNumber')
            address1 = tree2.find('.//Address1Text')
            address2 = tree2.find('.//Address2Text')
            accNumber = tree2.find('.//AccountNumber')
            accHolder = tree2.find('.//AccountHolder')
            bName = tree2.find('.//BankName')
            payCode = tree2.find('.//PayGroupCode')
            salCode = tree2.find('.//SalariedCode')
            emplId = tree2.find('.//EmploymentId')
            preFName = tree2.find('.//PreferredFirstName')
            preLName = tree2.find('.//PreferredLastName')
            try:
                fName.text = hashlib.md5(fName.text.encode('utf-8')).hexdigest()
                lName.text = hashlib.md5(lName.text.encode('utf-8')).hexdigest()
                email.text = hashlib.md5(email.text.encode('utf-8')).hexdigest()
                phone.text = hashlib.md5(phone.text.encode('utf-8')).hexdigest()
                address1.text = hashlib.md5(address1.text.encode('utf-8')).hexdigest()
                address2.text = hashlib.md5(address2.text.encode('utf-8')).hexdigest()
                accNumber.text = hashlib.md5(accNumber.text.encode('utf-8')).hexdigest()
                accHolder.text = hashlib.md5(accHolder.text.encode('utf-8')).hexdigest()
                bName.text = hashlib.md5(bName.text.encode('utf-8')).hexdigest()
                payCode.text = hashlib.md5(payCode.text.encode('utf-8')).hexdigest()
                salCode.text = hashlib.md5(salCode.text.encode('utf-8')).hexdigest()
                emplId.text = hashlib.md5(emplId.text.encode('utf-8')).hexdigest()
                preFName.text = hashlib.md5(preFName.text.encode('utf-8')).hexdigest()
                preLName.text = hashlib.md5(preLName.text.encode('utf-8')).hexdigest()
            except AttributeError:
                pass

            tree2.write(open(newFile, 'wb'), encoding='UTF-8', xml_declaration=True)
        return file2Check

def getTheGcid(iFile):
    GCID = []
    with open(iFile, 'rt', encoding='utf-8') as f:
        tree = ElementTree.parse(f)
        for node in tree.findall('.//Colleague'):  #
            collId = node.find('.//GlobalColleagueId')
            GCID.extend(collId)
    return GCID

def compareColleagueXML(ala, boomi):
    return filecmp.cmp(ala, boomi)


def email_report(inMessHtml, inMessText, inAttach):
    ## check the directory in which formOutbound is running in.
    COMMASPACE = ', '
    cwd = os.getcwd()
    ## read configuration file and check filename pattern
    config = configparser.ConfigParser()
    config.sections()
    _iniFile = cwd + '\\ala2boomi.ini'
    iniFile = _iniFile.replace("\\", "\\\\")
 #   print("Reading the Configuration file " + iniFile + "\n ")
    config.read(iniFile)
    gAccount = config['DIR']['sender_gemail_address']
    gPass = config['DIR']['sender_gemail_password']
    email_target = config['DIR']['target_receivers']

    sender = gAccount
    gmail_password = gPass
    recipients = email_target.split(",")
    print(recipients)
    # Create the enclosing (outer) message
    outer = MIMEMultipart()
    outer['Subject'] = 'Test Report: Colleague Integration Migration 2 ReLaX'
    outer['To'] = COMMASPACE.join(recipients)
   ## outer['To'] = .join(recipients)
    outer['From'] = sender
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
    text = inMessText
    html = inMessHtml

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    outer.attach(part1)
    outer.attach(part2)

    # List of attachments
    attachments = [inAttach]

    # Add the attachments to the message
    for file in attachments:
        try:
            with open(file, 'rb') as fp:
                msg = MIMEBase('application', "octet-stream")
                msg.set_payload(fp.read())
            encoders.encode_base64(msg)
            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
            outer.attach(msg)
        except:
            print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
            raise

    composed = outer.as_string()

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()

            s.login(sender, gmail_password)
            s.sendmail(sender, recipients, composed)
            s.close()
        print("Email sent!")
    except:
        print("Unable to send the email. Error: ", sys.exc_info()[0])
        raise


## check the directory in which formOutbound is running in.
cwd = os.getcwd()
## read configuration file and check filename pattern
config = configparser.ConfigParser()
config.sections()
_iniFile = cwd + '\\ala2boomi.ini'
iniFile = _iniFile.replace("\\", "\\\\")
print("Reading the Configuration file " + iniFile + "\n ")
config.read(iniFile)
## read the directory for the inbound files
## take absolut path

_inDir = config['DIR']['ALAOutbound']
_outDir = config['DIR']['BoomiOutbound']
_tmpInDir = config['DIR']['ALALocal']
_tmpOutDir = config['DIR']['BoomiLocal']

## prepare the outbound folder
## loop in the inbound folder list the inbound files
_message =[]
count = 0
print("Start comparision")
print("====Clear ALA Temp folders =======>>")
for path, subdirs, files in os.walk(_tmpInDir):
    for name in files:
        os.remove(os.path.join(path, name))

print("====Clear BOOMI Temp folders =======>>")

for path, subdirs, files in os.walk(_tmpOutDir):
    for name in files:
        os.remove(os.path.join(path, name))

print("====Get the files from ALA to Compare =======>>")
_qFil2Analy = config['DIR']['File2Analyse']

print("The last " + _qFil2Analy + " ALA files will be analysed by the script")

alaFiles = []
bFiles = []
## here instead of checking a particular number of files
## the script must check yesterdays folder files to be compared
##  YYYY
##    |
##    |--YYYYMM
##          |
##          |--YYYYMMDD
##                  |
##                  |
##                  |--file001.xml
##                  |--file002.xml

_yesterday = datetime.date.today() - datetime.timedelta(1)
yesterday = _yesterday.strftime("%Y%m%d")
month = _yesterday.strftime("%Y%m")
year = _yesterday.strftime("%Y")

_inDir = _inDir + "\\" + year + "\\" + month +  "\\" + yesterday
_outDir = _outDir + "\\" + year + "\\" + month +  "\\" + yesterday

print(_inDir)
print(_outDir)

if (os.path.isdir(_inDir) & os.path.isdir(_outDir)):

    for path, subdirs, files in os.walk(_inDir):
        for name in files:
            pass
            alaFiles.append(os.path.join(path, name))
    for path, subdirs, files in os.walk(_outDir):
        for name in files:
            pass
            bFiles.append(os.path.join(path, name))

    count = 0
    count2 = int(_qFil2Analy)  ## shouold be removed
    alaFiles.reverse()
    bFiles.reverse()
    alaNews = []
    boomiOlds = []
    print("The last " + str(count2) + " Boomi files will be used to compare")
    print("Loop in the files to compare")

    s = set(boomiOlds)

    _cvsFile = config['DIR']['logFileDir'] + "\\" + "AlaColleagueTestComparision.csv"
    _cvsFile = _cvsFile.replace("\\", "\\\\")
    print("test comparision written to: " + _cvsFile)
    testResult = 0
    testResult2 = 0

##   if len(alaNews) >= len(boomiOlds):
##      pass
##        tmpMess = "There are: "  + len(alaNews) +  " ReLaX "
##        _message.append()
##
##    else:
##        testResult2 = -1
##        print("<<<####### " + str(len(alaNews)) + " Ala files != " + str(len(boomiOlds)) + " #######>>>")
    print("====Get the files from Boomi to Compare =======>>")
    for f in alaFiles:
        alaNews.extend(copySingleMessages(f, _tmpInDir))
    for f in bFiles:
        boomiOlds.extend(copySingleMessages(f, _tmpOutDir))

    alaNews = set(alaNews)
    boomiOlds = set(boomiOlds)
    successCounter = 0
    failCounter = 0
    notInRelCounter = 0
    boomiCount = 0
    alamess = len(alaNews)
    with open(_cvsFile, 'w') as csvfile:
        fieldnames = ['ala_file', 'boomi_file', 'result']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for f in boomiOlds:
            boomiCount = boomiCount + 1
            fa = f.replace(_tmpOutDir, _tmpInDir)
            if fa in alaNews:
                if (compareColleagueXML(f, fa)):
                    # log to file
                    writer.writerow({'ala_file': f, "boomi_file": fa, "result": "true"})
                    successCounter = + successCounter + 1
                    pass
                else:
                    # log to file not equal
                    writer.writerow({'ala_file': f, "boomi_file": fa, "result": "fail"})
                    testResult = -1
                    failCounter = failCounter + 1
                    pass
            else:
                pass
                # log to file not found
                writer.writerow({'ala_file': f, "boomi_file": fa, "result": "not In ReLaX!"})
                testResult = -1
                notInRelCounter = notInRelCounter + 1




    _inBakground = config['DIR']['runInBakground']

## get even the GCID to compare and add to the email to be send.
    if (_inBakground == "true"):
        if (testResult == 0 and testResult2 == 0):
            html_message = """\
            <html><header><title>Message Statistics</title></header><body><p>Message Statistics</p>
                <table border="1" >
                <colgroup span="4"></colgroup>
                  <tr>
                    <th>Boomi Messages</th>
                    <th>ReLax Messages</th>
                    <th>Relax On Success</th>
                    <th>Relax failed</th>
                    <th>Relax Missing</th>
                  </tr>    
                  <tr>
                    <td>""" + str(boomiCount) + "</td>" + "<td>" + str(alamess) + "</td>" + "<td>" + str(successCounter) + "</td>"  +  "<td>" +  str(failCounter) + "</td>" +  "<td>" + str(notInRelCounter) + "</td></tr></table></body></html>"
            text_message = "THE TEST PASSED!!!"
            email_report(html_message, text_message, _cvsFile)
        else:
            html_message = """\
            <html><header><title>Message Statistics</title></header><body><p>Message Statistics</p>
                <table border="1" >
                <colgroup span="4"></colgroup>
                  <tr>
                    <th>Boomi Messages</th>
                    <th>ReLax Messages</th>
                    <th>Relax On Success</th>
                    <th>Relax failed</th>
                    <th>Relax Missing</th>
                  </tr>    
                  <tr>
                    <td>""" + str(boomiCount) + "</td>" +  "<td>" + str(alamess) + "</td>" + "<td>" + str(successCounter) + "</td>"  +  "<td>" +  str(failCounter) + "</td>" +  "<td>" + str(notInRelCounter) + "</td></tr></table></body></html>"
            text_message = "THE TEST FAILED!!!"
            email_report(html_message, text_message, _cvsFile)

    else:
        if (testResult == 0 and testResult2 == 0):
            print("<<<######################################################>>>")
            print()
            print("               <<<   The Test PASSED!!!   >>>")
            print()
            print("<<<######################################################>>>")
            root = tk.Tk()
            app = Feedback(master=root)
            app.mainloop()
        else:
            print("<<<######################################################>>>")
            print()
            print("               <<<   THE TEST FAILED!!!   >>>")
            print()
            print("<<<######################################################>>>")
            root = tk.Tk()
            app = Feedback2(master=root)
            app.mainloop()

else:
    _inBakground = config['DIR']['runInBakground']
    if (_inBakground == "true"):
        pass
    else:
        print("<<<######################################################>>>")
        print()
        print("               <<<   THE TEST FAILED!!!   >>>")
        print()
        print("  <<<Either Boomi or ReLaX didn't deliver files   >>>")
        print("<<<######################################################>>>")
        root = tk.Tk()
        app = Feedback2(master=root)
        app.mainloop()

