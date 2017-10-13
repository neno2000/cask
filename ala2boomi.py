# import re
import configparser
import tkinter as tk
from tkinter import *
import os
import filecmp
from xml.etree import ElementTree
import csv
import hashlib


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
    files2Check = []
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
            newFile = iTmpFolder + "\\" + timeSt.text + "_" + collId.text + "_" + batchType
            newFile = newFile.replace(":", "_")
            newFile = newFile.replace(".", "_")
            newFile = newFile.replace("C_", "C:")
            newFile = newFile + ".xml"
            files2Check.append(newFile)
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
            #ElementTree.dump(tree2)
            ##end has data
            tree2.write(open(newFile, 'wb'), encoding='UTF-8', xml_declaration=True)
        return files2Check


def compareColleagueXML(ala, boomi):
    return filecmp.cmp(ala, boomi)


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

for path, subdirs, files in os.walk(_inDir):
    for name in files:
        pass
        alaFiles.append(os.path.join(path, name))
for path, subdirs, files in os.walk(_outDir):
    for name in files:
        pass
        bFiles.append(os.path.join(path, name))

count = 0
count2 = int(_qFil2Analy) + 10  ## shouold be removed
alaFiles.reverse()
bFiles.reverse()
alaNews = []
boomiOlds = []

print("====Get the files from Boomi to Compare =======>>")
for f in alaFiles:
    if count < int(_qFil2Analy):
        alaNews.extend(copySingleMessages(f, _tmpInDir))
        count = count + 1
    ##    count2 = count2 + 1
    ##    boomiOlds.extend(copySingleMessages(f, _tmpOutDir))
    else:
        break
count = 0
for f in bFiles:
    if count < count2:
        boomiOlds.extend(copySingleMessages(f, _tmpOutDir))
        count = count + 1
    ##    count2 = count2 + 1
    ##    boomiOlds.extend(copySingleMessages(f, _tmpOutDir))
    else:
        break

print("The last " + str(count2) + " Boomi files will be used to compare")
print("Loop in the files to compare")

s = set(boomiOlds)

_cvsFile = config['DIR']['logFileDir'] + "\\" + "AlaColleagueTestComparision.csv"
_cvsFile = _cvsFile.replace("\\", "\\\\")
print("test comparision written to: " + _cvsFile)
testResult = 0
testResult2 = 0

if len(alaNews) == len(boomiOlds):
    pass
else:
    testResult2 = -1
    print("<<<####### " + str(len(alaNews)) + " Ala files != " +  str(len(boomiOlds)) + " #######>>>")

with open(_cvsFile, 'w') as csvfile:
    fieldnames = ['ala_file', 'boomi_file', 'result']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for f in alaNews:
        fa = f.replace(_tmpInDir, _tmpOutDir)
        # fa = (fa.replace("\\", "\\\\"))
        ## print(fa)
        if fa in boomiOlds:

            if (compareColleagueXML(f, fa)):
                # log to file
                writer.writerow({'ala_file': f, "boomi_file": fa, "result": "true"})
                pass
            else:
                # log to file not equal
                writer.writerow({'ala_file': f, "boomi_file": fa, "result": "fail"})
                testResult = -1
                pass
        else:
            pass
            # log to file not found
            writer.writerow({'ala_file': f, "boomi_file": fa, "result": "notInBoomi!"})
            testResult = -1

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
