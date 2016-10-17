#*************************************************************
# CONTENT       informs project members about changes
#
# EMAIL         contact@richteralexander.com
#*************************************************************

import os
import sys
import time
import shutil
import logging

from threading import Thread
from datetime import datetime

from PySide import QtUiTools
from PySide.QtGui import *
from PySide.QtCore import *

# DELETE ******************
sys.path.append("../../settings")
import setEnv
setEnv.SetEnv()
import getProject
s = getProject.GetProject()
from lib import libLog
#**************************

from lib import libImg
from lib import libFunc
from lib import libFileFolder


#************************
# REPORT
class Reminder:
    def __init__(self,
                 title = "arReminder Test",
                 msg = "This is just a Reminder Test - Dont do it again!",
                 userTo = "arichter",
                 topic = "info",
                 link = " ",
                 timer = " "):

        self.time       = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        self.active     = True    #message need to be send
        self.title      = str(title)   #Pipeline Update
        self.msg        = str(msg)     #New Features for Pipeline
        self.userfrom   = os.getenv('username') #user from
        self.userto     = userto  #user to
        self.topic      = topic   #PDF
        self.link       = link    #path
        self.timer      = timer   #time when reminder is triggert

    def __call__(self):
        return (\
        "time:     " + self.time + "\n" +\
        "active:   " + str(self.active) + "\n" + "\n" +\
        "userFrom: " + self.userfrom + "\n" +\
        "userTo:   " + self.userto + "\n" + "\n" +\
        "title:    " + self.title + "\n" +\
        "msg:      " + self.msg + "\n" + "\n" +\
        "topic:    " + self.topic + "\n" +\
        "link:     " + self.link + "\n" +\
        "timer:    " + self.timer + "\n")


#**********************
# DEFAULT
TITLE   = os.path.splitext(os.path.basename(__file__))[0]
LOG     = libLog.initLog(script=TITLE, level=logging.INFO)
PATH_UI = s.PATH["ui"] + TITLE + ".ui"

#**********************
# VARIABLE
TIME        = ""
LINK        = ""
READY       = False

TOPICS      = ["preview", "pdf", "report", "info", "pipeline", "publish"]
USER        = ["all", "core", "anim"]

PATH_IMG    = ""
PATH_FILE   = ""
REMINDER    = ""

#**********************
# PRESS_TRIGGER
def press_btnAccept():
    global LOG
    saveReminder()
    LOG.info("END : CREATE")
    WIDGET.close()


def press_btnCancel():
    global LOG, READY
    READY = True
    LOG.info("END : CANCEL")
    WIDGET.close()


def press_btnPreviewImg():
    global PATH_IMG
    PATH_IMG = PATH_IMG.replace("/", "\\")
    os.system(PATH_IMG)

#**********************
# CHANGE_TRIGGER
def change_cbxTo():
    libFunc.setUserImg(WIDGET.cbxTo.currentText().lower(), WIDGET.lblUserTo)


def change_cbxTopic():
    libFunc.setPreviewImg(WIDGET.cbxTopic.currentText().lower(), WIDGET.lblPreviewImg)


#**********************
# FUNCTION
def saveReminder():
    global TIME

    fileName = WIDGET.cbxTo.currentText().lower()

    if fileName == "core" or fileName == "all" or fileName == "anim":
        fileName = s.TEAM[fileName]

    setTimer = WIDGET.edtDate.dateTime().toString("yyyy.MM.dd hh:mm:ss")

    if WIDGET.edtDate.dateTime() == TIME:
        setTimer = ""

    fileName = (fileName,) if not isinstance(fileName, (tuple, list)) else fileName

    for member in fileName:
        reminder = Reminder(title = WIDGET.edtTitle.text(), msg = WIDGET.edtMsg.toPlainText(), userTo = member, topic = WIDGET.cbxTopic.currentText().lower(), link = WIDGET.edtImgLink.text(), timer =  setTimer)
        dataPath = s.PATH["data_reminder"] + '/' + member + '/' + TIME.toString("yyyy_MM_dd_hh_mm_ss") + s.FILE_FORMAT["data"]

        libFunc.createFolder(dataPath)
        libFileService.saveJsonFile(dataPath, reminder)

    LOG.info("CREATE : REMINDER : " + WIDGET.edtTitle.text() + " + " + WIDGET.edtMsg.toPlainText())


#**********************
# INIT
def init():
    global REMINDER, PATH_FILE

    WIDGET.edtTitle.setText(REMINDER["title"])
    WIDGET.edtMsg.setPlainText(REMINDER["msg"])
    WIDGET.edtTime.setText(REMINDER["time"])

    libFunc.setUserImg(REMINDER["userfrom"], WIDGET.lblUserFrom)
    libFunc.setPreviewImg(REMINDER["topic"], WIDGET.lblPreviewImg)

    WIDGET.lblPreviewImg.setToolTip(REMINDER["link"])

    # PATH_FILE
    src = s.PATH["data_reminder"] + "/" + os.getenv('username') + "/" + PATH_FILE +  s.FILE_FORMAT["data"]
    dst = s.PATH["data_reminder"] + "/" + os.getenv('username') + "/" + s.STATUS["history"] + "/" + PATH_FILE + s.FILE_FORMAT["data"]
    # put into history
    libFunc.createFolder(dst)

    if(os.path.exists(src)):
        shutil.move(src, dst)


#**********************
# START PROZESS
def start(addReminder = False):
    global TITLE, TIME, REMINDER, PATH_FILE

    TIME     = QDateTime.currentDateTime()
    PATH_IMG = libImg.rmTempImg()

    app      = QApplication(sys.argv)
    WIDGET   = QtUiTools.QUiLoader().load(PATH_UI)

    if addReminder:
        WIDGET.edtMsg.clear()
        WIDGET.cbxTopic.clear()
        WIDGET.edtTitle.clear()

        WIDGET.cbxTopic.addItems(TOPICS)
        WIDGET.cbxTo.addItems(USER)
        WIDGET.cbxTo.addItems(s.TEAM["core"])
        WIDGET.edtTitle.setEnabled(True)
        WIDGET.edtMsg.setEnabled(True)
        libFunc.setUserImg(os.getenv('username'), WIDGET.lblUserFrom)

        WIDGET.edtDate.setDateTime(TIME)

        PATH_FILE = libFileService.getFolderList(s.PATH["data_reminder"] + "/" + os.getenv('username'), "*.json")[0]
        REMINDER  = libFileService.loadJsonFile(s.PATH["data_reminder"] + "/" + os.getenv('username') + "/" + PATH_FILE + s.FILE_FORMAT["data"])

        WIDGET.connect(WIDGET.btnAccept, SIGNAL("clicked()"), press_btnAccept)
        WIDGET.connect(WIDGET.btnCancel, SIGNAL("clicked()"), press_btnCancel)
        WIDGET.connect(WIDGET.btnPreviewImg, SIGNAL("clicked()"), press_btnCancel)

        WIDGET.connect(WIDGET.cbxTo, SIGNAL("currentIndexChanged(const QString&)"), change_cbxTo)
        WIDGET.connect(WIDGET.cbxTopic, SIGNAL("currentIndexChanged(const QString&)"), change_cbxTopic)

    else:
        WIDGET.cbxTo.hide()
        WIDGET.edtDate.hide()
        WIDGET.cbxTopic.hide()
        WIDGET.btnAccept.hide()
        WIDGET.edtImgLink.hide()
        WIDGET.lblUserTo.hide()

        WIDGET.edtTitle.setEnabled(False)
        WIDGET.edtMsg.setEnabled(False)
        WIDGET.lblPreviewImg.mousePressEvent = press_lblPreviewImg
        init()

    WIDGET.connect(WIDGET.btnPreviewImg, SIGNAL("clicked()"), press_btnPreviewImg)

    # WIDGET : delete border & always on top
    WIDGET.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)# | Qt.Tool)

    # WIDGET : move to right low corner
    resolution = QDesktopWidget().screenGeometry()
    WIDGET.move(resolution.width() - WIDGET.width() - 5, resolution.height() - WIDGET.height() - 5)

    WIDGET.show()
    app.exec_()

# def sleeper():
#     while True:

#         if len(libFileService.getFolderList(s.PATH["data_reminder"] + "/" + os.getenv('username'), "*.json")) > 0:
#             print "START : " + libFileService.getFolderList(s.PATH["data_reminder"] + "/" + os.getenv('username'), "*.json")[0]
#             start()

#             print "SLEEPY"

#             while not READY:
#                 time.sleep(10000)

# def reminderLoop():
#     t = Thread(target=sleeper)
#     t.start()

# startReminder()
# from utilities import arReminder
# reload(arReminder)
# arReminder.reminderLoop()


start()
