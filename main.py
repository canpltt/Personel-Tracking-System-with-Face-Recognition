#!/usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------
#                - General & Graphical Library -
#--------------------------------------------------------------------
import sys
import os
import threading
import time

import numpy as np
import cv2
import sqlite3
import utils, math
import mediapipe as mp
import pickle
import logging
import face_recognition
import winsound

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QMainWindow
from PyQt5.QtGui import QPixmap, QRegExpValidator
from PyQt5.QtCore import QTimer,Qt, QRegExp
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QIcon

#-----------------------------------------------------------------------
#                      - General  Path Definition -
#-----------------------------------------------------------------------
from deepface import DeepFace

HomeDirectoryPath       = os.getcwd()
UiDirectoryPath         = os.path.realpath('FileUi')
ImagesDirectoryPath     = os.path.realpath('Images')
PersonListPath          = os.path.realpath('PersonList')
AdminListDatabasePath   = os.path.realpath('UsernamePassword.db')
LogoImagePath           = os.path.join(ImagesDirectoryPath, "logo.png")
PicturePersonPath       = os.path.join(ImagesDirectoryPath, "person.png")
HomeWindowIconPath      = os.path.join(ImagesDirectoryPath, "eye.png")

#-----------------------------------------------------------------------
#                      - Screen Path Definition -
#-----------------------------------------------------------------------


WelcomScreenPath          = os.path.join(UiDirectoryPath, "welcomescreen.ui")
LoginScreenPath           = os.path.join(UiDirectoryPath, "AdminPaneliGiris.ui")
SetScreenPath             = os.path.join(UiDirectoryPath, "AdminPaneli.ui")
AddAdminPath              = os.path.join(UiDirectoryPath, "YeniAdminKayit.ui")
AddPersonelScreenPath     = os.path.join(UiDirectoryPath, "PersonelKayitVeritabani.ui")
AddCameraScreenPath       = os.path.join(UiDirectoryPath, "KameraKaydet.ui")
ReportSetScreenPath       = os.path.join(UiDirectoryPath, "RaporlamaAyar.ui")
PerformansWatchScreenPath = os.path.join(UiDirectoryPath, "PerformansTakip.ui")
DeleteCameraScreenPath    = os.path.join(UiDirectoryPath, "KameraSilme.ui")
DeletePersonelScreenPath  = os.path.join(UiDirectoryPath, "PersonelSilme.ui")
CameraWatchScreenPath     = os.path.join(UiDirectoryPath, "KameraIzleme.ui")


#-----------------------------------------------------------------------
#                    - Directory Path Definition -
#-----------------------------------------------------------------------

PersonelPictureDirectory  = os.path.join(HomeDirectoryPath, "PersonList")
DataLoggerDirectory       = os.path.join(HomeDirectoryPath, "DataLogger")
DataLoggerFilePath        = os.path.join(DataLoggerDirectory, "GunlukRapor.xlsx")

#-----------------------------------------------------------------------
#                    - Creating Directory Process -
#-----------------------------------------------------------------------
ControlExistsPersonel = os.path.exists(PersonelPictureDirectory)
if not ControlExistsPersonel:
  os.makedirs(PersonelPictureDirectory)
  print("[AKIN] PersonList Isimli Klasor Olusturuldu ")


ControlExistsDataLogger = os.path.exists(DataLoggerDirectory)
if not ControlExistsDataLogger:
  os.makedirs(DataLoggerDirectory)
  print("[AKIN]: DataLogger Isimli Klasor Olusturuldu ")


"""
w  write mode
r  read mode
a  append mode
w+  create file if it doesn't exist and open it in write mode
r+  open for reading and writing. Does not create file.
a+  create file if it doesn't exist and open it in append mode
"""
DataLoggerFile = open(DataLoggerFilePath, 'w+')
#print("[AKIN]: DataLoggerFile Isimli Dosya Olusturuldu ")


#--------------------------------------------------------------------
#              - Face Recognition Libraryes -
#--------------------------------------------------------------------


#--------------------------------------------------------------------
#                  - Date And Time Library -
#--------------------------------------------------------------------

from datetime import datetime

#--------------------------------------------------------------------
#               - Email Send Settings And Libraries -
#--------------------------------------------------------------------



#--------------------------------------------------------------------
#                  - Date And Time Functions  -
#--------------------------------------------------------------------


def ReadNowTime():
    """
    This Function Reads Current Time And Return
    """
    now = datetime.now()
    Time = now.strftime("%H:%M:%S")
    #DateTime = now.strftime("%d/%m/%Y %H:%M:%S")
    #print(Time)
    return Time


def ReadNowDate():
    """
    This Function Reads Current Date And Return
    """
    now = datetime.now()
    Date = now.strftime("%d/%m/%Y")
    #print(Date)
    return Date



def ReadDateAndTime():
    """
    This Function Reads Current Date And Time
    For Log
    """
    now = datetime.now()
    DateTime = now.strftime("%d/%m/%Y %H:%M:%S")
    #print(DateTime)
    return  DateTime

#--------------------------------------------------------------------
#                 - HomePage  Screen  Settings -
#--------------------------------------------------------------------

class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi(WelcomScreenPath,self)
        self.logo.setPixmap(QPixmap("Images/fot-logo.png"))
        self.setGeometry(0, 0, 400, 300)
        self.AdminPanel.clicked.connect(self.gotologin)

        # set control_bt callback clicked  function
        self.open.clicked.connect(self.controlTimer)

        self.addCamera.clicked.connect(self.CameraAdd)
        self.dltCamera.clicked.connect(self.CameraDelete)
        self.showCamera.clicked.connect(self.CameraShow)


        self.Date.setText(ReadNowDate())

        #########################################################################################

        self.simple_format = '%(asctime)s - %(name)s - %(message)s'  # Log kayıt biçimi

        logging.basicConfig(
            filename='Logfile.log',
            filemode='a',
            format=self.simple_format,
            level=logging.INFO,
            datefmt='%d.%m.%y - %H.%M'
        )
        self.logger = logging.getLogger('Giriş')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(self.simple_format)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        ################################ Kamera Kayıtları ####################################
        file = open('cameras.pkl', 'rb')  # Kamera kayıtlarını al
        self.cameras = pickle.load(file)
        file.close()
        self.camera_Name_List = []
        self.camera_Adress_List = []
        i = 0
        for camera in self.cameras:  # Kamera kayıtlarını listeye kaydet
            self.camera_Name_List.append(camera)
            self.camera_Adress_List.append(self.cameras[camera])
            self.comboBox.addItem(self.camera_Name_List[i])
            i += 1
        ################################ Kullanıcı Kayıtları ##################################
        file = open('encoding_data.pkl', 'rb')  # Önceki kayıtları al
        self.veriler = pickle.load(file)
        file.close()
        self.kisiler = list(self.veriler.keys())

        self.named1 = "Tanimlaniyor"
        self.named2 = "Tanimlaniyor"
        self.named3 = "Tanimlaniyor"
        self.named4 = "Tanimlaniyor"
        self.named5 = "Tanimlaniyor"
        self.named6 = "Tanimlaniyor"
        self.named7 = "Tanimlaniyor"
        self.named8 = "Tanimlaniyor"
        self.named9 = "Tanimlaniyor"
        ########################################################################################
        self.timer_name = 18
        self.timer_screenshot = 50

        self.dokontrol = True

        self.pen.mousePressEvent = self.buyut1
        self.pen_2.mousePressEvent = self.buyut2
        self.pen_3.mousePressEvent = self.buyut3
        self.pen_4.mousePressEvent = self.buyut4
        self.pen_5.mousePressEvent = self.buyut5
        self.pen_6.mousePressEvent = self.buyut6
        self.pen_7.mousePressEvent = self.buyut7
        self.pen_8.mousePressEvent = self.buyut8
        self.pen_9.mousePressEvent = self.buyut9
        ########################################################################################
        self.pen.setVisible(False)
        self.pen_2.setVisible(False)
        self.pen_3.setVisible(False)
        self.pen_4.setVisible(False)
        self.pen_5.setVisible(False)
        self.pen_6.setVisible(False)
        self.pen_7.setVisible(False)
        self.pen_8.setVisible(False)
        self.pen_9.setVisible(False)

        self.dizi_name = [self.named1, self.named2, self.named3, self.named4,self.named5, self.named6, self.named7, self.named8,self.named9]
        self.dizi_screen = [self.pen, self.pen_2, self.pen_3, self.pen_4,self.pen_5,self.pen_6,self.pen_7,self.pen_8,self.pen_9]
        self.pen.mousePressEvent = self.buyut1

    def buyut1(self, event):
        if(self.dokontrol==True):
            self.pen.setGeometry(10, 10,1300,970)
            self.dokontrol=False
            for i in range(len(self.dizi_screen)):
                if i==0:
                    continue
                else:
                    self.dizi_screen[i].setVisible(False)
        else:
            self.dokontrol = True
            self.CameraShow()

    def buyut2(self, event):
        if(self.dokontrol==True):
            self.pen_2.setGeometry(10, 10, 1300, 970)
            self.dokontrol = False
            for i in range(len(self.dizi_screen)):
                if i == 1:
                    continue
                else:
                    self.dizi_screen[i].setVisible(False)
        else:
            self.dokontrol = True
            self.CameraShow()

    def buyut3(self, event):
        if (self.dokontrol == True):
            self.pen_3.setGeometry(10, 10, 1300, 970)
            self.dokontrol = False
            for i in range(len(self.dizi_screen)):
                if i == 2:
                    continue
                else:
                    self.dizi_screen[i].setVisible(False)
        else:
            self.dokontrol = True
            self.CameraShow()

    def buyut4(self, event):
        if (self.dokontrol == True):
            self.pen_4.setGeometry(10, 10, 1300, 970)
            self.dokontrol = False
            for i in range(len(self.dizi_screen)):
                if i == 3:
                    continue
                else:
                    self.dizi_screen[i].setVisible(False)
        else:
            self.dokontrol = True
            self.CameraShow()

    def buyut5(self, event):
        if (self.dokontrol == True):
            self.pen_5.setGeometry(10, 10, 1300, 970)
            self.dokontrol = False
            for i in range(len(self.dizi_screen)):
                if i == 4:
                    continue
                else:
                    self.dizi_screen[i].setVisible(False)
        else:
            self.dokontrol = True
            self.CameraShow()

    def buyut6(self, event):
        if (self.dokontrol == True):
            self.pen_6.setGeometry(10, 10, 1300, 970)
            self.dokontrol = False
            for i in range(len(self.dizi_screen)):
                if i == 5:
                    continue
                else:
                    self.dizi_screen[i].setVisible(False)
        else:
            self.dokontrol = True
            self.CameraShow()

    def buyut7(self, event):
        if (self.dokontrol == True):
            self.pen_7.setGeometry(10, 10, 1300, 970)
            self.dokontrol = False
            for i in range(len(self.dizi_screen)):
                if i == 6:
                    continue
                else:
                    self.dizi_screen[i].setVisible(False)
        else:
            self.dokontrol = True
            self.CameraShow()

    def buyut8(self, event):
        if (self.dokontrol == True):
            self.pen_8.setGeometry(10, 10, 1300, 970)
            self.dokontrol = False
            for i in range(len(self.dizi_screen)):
                if i == 7:
                    continue
                else:
                    self.dizi_screen[i].setVisible(False)
        else:
            self.dokontrol = True
            self.CameraShow()

    def buyut9(self, event):
        if (self.dokontrol == True):
            self.pen_9.setGeometry(10, 10, 1300, 970)
            self.dokontrol = False
            for i in range(len(self.dizi_screen)):
                if i == 8:
                    continue
                else:
                    self.dizi_screen[i].setVisible(False)
        else:
            self.dokontrol = True
            self.CameraShow()


    def CameraAdd(self):
        self.cameraList.addItem(self.comboBox.currentText())

    def CameraDelete(self):
        listItem=self.cameraList.selectedItems()
        for item in listItem:
            self.cameraList.takeItem(self.cameraList.row(item))

    def CameraShow(self):
        for i in range(len(self.dizi_screen)):
            self.dizi_screen[i].setVisible(False)

        for i in range(len(self.cameraList)):
            self.dizi_screen[i].setVisible(True)

            if (len(self.cameraList) == 1):
                self.pen.setGeometry(10, 10, 1300, 970)
            elif (len(self.cameraList) == 2):
                self.pen.setGeometry(10, 230, 640,480)
                self.pen_2.setGeometry(670, 230, 640,480)
            elif (len(self.cameraList) == 3):
                self.pen.setGeometry(10, 10, 640, 480)
                self.pen_2.setGeometry(670, 10, 640, 480)
                self.pen_3.setGeometry(380, 500, 640, 480)
            elif (len(self.cameraList) == 4):
                self.pen.setGeometry(10, 10, 640, 480)
                self.pen_2.setGeometry(670, 10, 640, 480)
                self.pen_3.setGeometry(10, 500, 640, 480)
                self.pen_4.setGeometry(670, 500, 640, 480)
            elif (len(self.cameraList) == 5):
                self.pen.setGeometry(10, 10, 640, 480)
                self.pen_2.setGeometry(670, 10, 640, 480)
                self.pen_3.setGeometry(10, 520, 430, 440)
                self.pen_4.setGeometry(450, 520, 430, 440)
                self.pen_5.setGeometry(890, 520, 430, 440)
            elif (len(self.cameraList) == 6):
                self.pen.setGeometry(10, 20, 430, 450)
                self.pen_2.setGeometry(450, 20, 430, 450)
                self.pen_3.setGeometry(890, 20, 430, 450)
                self.pen_4.setGeometry(10, 510, 430, 450)
                self.pen_5.setGeometry(450, 510, 430, 450)
                self.pen_6.setGeometry(890, 510, 430, 450)
            elif (len(self.cameraList) == 7):
                self.pen.setGeometry(10, 50, 430, 450)
                self.pen_2.setGeometry(450, 50, 430, 450)
                self.pen_3.setGeometry(890, 50, 430, 450)
                self.pen_4.setGeometry(10, 590, 320, 330)
                self.pen_5.setGeometry(340, 590, 320, 330)
                self.pen_6.setGeometry(670, 590, 320, 330)
                self.pen_7.setGeometry(1000, 590, 320, 330)
            elif (len(self.cameraList) == 8):
                self.pen.setGeometry(10, 100, 320, 330)
                self.pen_2.setGeometry(340, 100, 320, 330)
                self.pen_3.setGeometry(670, 100, 320, 330)
                self.pen_4.setGeometry(1000, 100, 320, 330)
                self.pen_5.setGeometry(10, 590, 320, 330)
                self.pen_6.setGeometry(340, 590, 320, 330)
                self.pen_7.setGeometry(670, 590, 320, 330)
                self.pen_8.setGeometry(1000, 590, 320, 330)
            elif (len(self.cameraList) == 9):
                self.pen.setGeometry(10, 5, 410, 320)
                self.pen_2.setGeometry(450, 5, 410, 320)
                self.pen_3.setGeometry(890, 5, 410, 320)
                self.pen_4.setGeometry(10, 335, 410, 320)
                self.pen_5.setGeometry(450, 335, 410, 320)
                self.pen_6.setGeometry(890, 335, 410, 320)
                self.pen_7.setGeometry(10, 665, 410, 320)
                self.pen_8.setGeometry(450, 665, 410, 320)
                self.pen_9.setGeometry(890, 665, 410, 320)


    def kontrol(self,number):
        tanima=False
        try:
            testImage = face_recognition.load_image_file(self.filepath)
            faceLocations = face_recognition.face_locations(testImage)
            faceEncodings = face_recognition.face_encodings(testImage, faceLocations)
            dist = 0
            for j in range(len(self.veriler)):
                for k in range(len(self.veriler[self.kisiler[j]])):
                    for i in range(128):
                        dist += (self.veriler[self.kisiler[j]][k][i] - faceEncodings[0][i]) ** 2
                    sonuc = math.sqrt(dist)
                    if sonuc < 0.4:
                        self.dizi_name[number]=self.kisiler[j]
                        self.logger.info(self.dizi_name[number])
                        tanima=True
                        ###################### Duygu Tanıma ######################
                        try:
                            predictions = DeepFace.analyze(testImage, actions=['emotion'])
                            self.Status.setText(predictions['dominant_emotion'])
                        except:
                            self.Status.setText("Duygu Bulunamadı")
                        ##########################################################

                        demography = DeepFace.analyze(testImage)

                        print("Yaş: ", demography["age"])
                        print("Cinsiyet: ", demography["gender"])
                        print("Duygu: ", demography["dominant_emotion"])
                        print("Irk/etnisite: ", demography["dominant_race"])

                        break
                    dist = 0
            if tanima==False:
                self.dizi_name[number]="Taninmadi"
        except:
            self.dizi_name[number]="Yuz Bulanamadi"

        new_name = self.image_name + "-" + self.dizi_name[number]

        os.rename('Images/{}.png'.format(self.image_name), 'Images/{}.png'.format(new_name))

    def take_screenshot(self,number):
        path, dirs, files = next(os.walk("Images"))
        self.image_name = "{}.{}.{}-{}.{}.{}".format(str(self.saat), str(self.dakika), str(self.saniye), str(self.gun),
                                                     str(self.ay), str(self.yil))

        self.filepath = os.path.join("Images/{}.png".format(self.image_name))
        cv2.imwrite(self.filepath, self.face)
        self.kontrol(number)

    def controlTimer(self):
        items = []
        thread_array=["t1","t2","t3","t4","t5","t6","t7","t8","t9"]
        camera_array=[]
        for i in range(len(self.cameraList)):
            thread_array[i] = threading

        for index in range(self.cameraList.count()):
            items.append(self.cameraList.item(index).text())

        for i in range(len(items)):
            camera_array.append(self.camera_Adress_List[self.camera_Name_List.index(items[i])])

        if self.open.text()=="Baslat":
            self.watch=True

            for i in range(len(self.cameraList)):
                thread_array[i].Thread(target=self.calistir,args=(i,camera_array[i])).start()

            self.open.setText("Durdur")
        else:
            self.watch=False
            self.open.setText("Baslat")


    def calistir(self,number,kamera):
        try:
            cap = cv2.VideoCapture(kamera)
            face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            self.genis=self.dizi_screen[number].width()
            self.yuksek=self.dizi_screen[number].height()
            while self.watch:
                ret, frame = cap.read()
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = face_classifier.detectMultiScale(gray, 1.3, 5)
                if (self.timer_name == 0):
                    self.dizi_name[number] = "Tanimlaniyor"
                    self.timer_name = 18
                else:
                    self.timer_name -= 1

                now = datetime.now()
                for (x, y, w, h) in faces:
                    cropped_faces = image[y:y + h, x:x + w]
                    color = (255, 255, 0)
                    stroke = 2
                    width = x + w
                    height = y + h
                    cv2.rectangle(image, (x, y), (width, height), color, stroke)
                    self.timer_screenshot -= 1
                    self.face = cv2.resize(cropped_faces, (200, 200))
                    self.face = cv2.cvtColor(self.face, cv2.COLOR_BGR2GRAY)

                    if self.dizi_name[number] == "Tanimlaniyor":
                        cv2.rectangle(image, (x, y), (width, height), (255, 255, 0), stroke)
                        cv2.putText(image, f'{self.dizi_name[number]}', (x, y - 20), cv2.FONT_HERSHEY_PLAIN,
                                    2, (255, 255, 0), 2)
                    elif self.dizi_name[number] == "Taninmadi":
                        cv2.rectangle(image, (x, y), (width, height), (255, 0, 0), stroke)
                        cv2.putText(image, f'{self.dizi_name[number]}', (x, y - 20), cv2.FONT_HERSHEY_PLAIN,
                                    2, (255, 0, 0), 2)
                    else:
                        cv2.rectangle(image, (x, y), (width, height), (0, 255, 0), stroke)
                        cv2.putText(image, f'{self.dizi_name[number]}', (x, y - 20), cv2.FONT_HERSHEY_PLAIN,
                                    2, (0, 255, 0), 2)

                    if (self.timer_screenshot == 0):
                        self.gun = now.day
                        self.ay = now.month
                        self.yil = now.year
                        self.saat = now.hour
                        self.dakika = now.minute
                        self.saniye = now.second
                        self.timer_screenshot = 30
                        self.take_screenshot(number)

                ############################## Görüntü Boyutları ######################################
                self.up_width = self.dizi_screen[number].width()
                self.up_height = self.dizi_screen[number].height()
                up_points = (self.up_width, self.up_height)
                image = cv2.resize(image, up_points, interpolation=cv2.INTER_LINEAR)

                height, width, channel = image.shape
                step = channel * width
                qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
                self.dizi_screen[number].setPixmap(QPixmap.fromImage(qImg))
        except:
            print(number,"patladı")
            self.calistir(number,kamera)

    def hareket(self):
        ret, frame1 = self.cap.read()
        ret, frame2 = self.cap.read()

        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
                (x, y, w, h) = cv2.boundingRect(contour)

                if cv2.contourArea(contour) < 900:
                    continue
                cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

        up_width = 640
        up_height = 480
        up_points = (up_width, up_height)
        image = cv2.resize(frame1, up_points, interpolation=cv2.INTER_LINEAR)

        height, width, channel = image.shape
        step = channel * width
        qImg = QImage(image.data, width, height, step, QImage.Format_BGR888)
        self.pen.setPixmap(QPixmap.fromImage(qImg))

    def gotologin(self):
        widget.setFixedHeight(731)
        widget.setFixedWidth(1200)
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

        #self.image.setPixmap(QPixmap(LogoImagePath))


    def SaveInputLog(self):

        """
        bu alanda giriş yapılan loglar tutulacak

        tekrar bak !!!!!!!!!!!!!!!!!!!!!!
        """
        InputLog = "[LOG]: " + str(ReadNowDate()) +"| "+ str(ReadNowTime()+ "| "+ self.name + "| GIRIS YAPILDI")
        self.Status.setText("Giriş Başarılı")
        print( "-----------------[AKIN TECHNOLOGY FILE LOG SYSTEM ]-------------------")
        print( InputLog)




    def SaveOutputLog(self):
        """
        bu alanda cıkış yapılacak loglar tutulacak
        buraya dön !!!!!!!!!!!!!!!!!!!!!!
        """

        OutputLog = "[LOG]: " + str(ReadNowDate()) +"| "+ str(ReadNowTime()+ "| "+ self.name + "| ÇIKIS YAPILDI")

        self.Status.setText("Cıkış Başarılı")
        print("-----------------[AKIN TECHNOLOGY FILE LOG SYSTEM]:--------------------")
        print(OutputLog)


#--------------------------------------------------------------------
#                 - Login  Screen  Settings -
#--------------------------------------------------------------------


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi(LoginScreenPath,self)
        self.back.clicked.connect(self.gotomain)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
        self.image.setPixmap(QPixmap(LogoImagePath))

    def loginfunction(self):
        self.user = self.emailfield.text()
        self.password = self.passwordfield.text()

        conn = sqlite3.connect(AdminListDatabasePath)
        cur = conn.cursor()

        kontrol = 'SELECT * FROM login_info'
        cur.execute(kontrol)
        self.users = cur.fetchall()

        a=0
        if self.user != "" or self.password != "":
            for i in range(len(self.users)):
                if(self.user==self.users[i][0] and self.password==self.users[i][1]):
                    a+=1

            if a==1:
                print("[AKIN]: Sisteme Giris Basarılı.")
                self.GoToSet()
            else:
                self.eror.setText("Kullanıcı Kaydı Bulunamadı")
        else:
            self.eror.setText("Lütfen Sizden İstenen Bütün Alanları Doldurunuz.")

    def GoToSet(self):
        Set = SetScreen()
        widget.addWidget(Set)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def gotomain(self):
        widget.setFixedHeight(990)
        widget.setFixedWidth(1670)
        login = WelcomeScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.image.setPixmap(QPixmap(LogoImagePath))


#--------------------------------------------------------------------
#                 - Set  Screen  Settings -
#--------------------------------------------------------------------

class SetScreen(QDialog):
    def __init__(self):
        super(SetScreen, self).__init__()
        loadUi(SetScreenPath,self)
        widget.setFixedSize(1200, 730)
        self.setWindowIcon(QIcon(HomeWindowIconPath))
        self.setGeometry(0, 0, 400, 300)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.logo.setPixmap(QPixmap(LogoImagePath))
        self.back1.clicked.connect(self.gotomain)
        self.PersonelAdd.clicked.connect(self.PersonelAddFunc)
        self.AdminAdd.clicked.connect(self.AdminAddFunc)
        self.AddCam.clicked.connect(self.AddCamera)
        self.Setting.clicked.connect(self.SettingReport)
        self.PerformansWatch.clicked.connect (self.PerformansState)
        self.DeleteCamera.clicked.connect (self.CameraDelete)
        self.DeletePerson.clicked.connect (self.DeletePersonel)

    def SettingReport(self):
        login = SetReport()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def CameraDelete(self):
        login = DeleteCamera()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def AddCamera(self):
        login = CameraAdd()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)



    def AdminAddFunc(self):
        login = AdminAdd()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def PersonelAddFunc(self):
        login = PersonelAdd()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotomain(self):
        widget.setFixedHeight(990)
        widget.setFixedWidth(1670)
        login = WelcomeScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def PerformansState(self):
        """
        Performans sayfası eklenecek
        """
        login = PerformWatch()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def DeletePersonel(self):
        """
        Veri tabanından akullanıcı silmek için yazıldı
        """
        login = PersonelDelete()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)


#--------------------------------------------------------------------
#                 - Add Admin  Screen  Settings -
#--------------------------------------------------------------------


class AdminAdd(QDialog):
    def __init__(self):
        super(AdminAdd, self).__init__()
        loadUi(AddAdminPath ,self)
        widget.setFixedSize(1021,731)
        self.logo.setPixmap(QPixmap(LogoImagePath))
        self.back.clicked.connect(self.GoToAdminPanel)
        self.SaveAdmin.clicked.connect(self.AddAdminDatabase)


    def GoToAdminPanel(self):
        login = SetScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def AdminAddFunc(self):
        login = AdminAdd()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def AddAdminDatabase(self):
        UserName        = self.UserName.text()
        Password        = self.Pasword.text()
        ConfirmPassword = self.ConfirmPasword.text()

        if UserName == "" or Password == "" or ConfirmPassword == "":
            self.ErorLabel.setText("Lütfen Sizden İstenilen Bütün Alanları Doldurunuz.")

        else:
            conn = sqlite3.connect(AdminListDatabasePath)
            cur = conn.cursor()
            sql = """INSERT INTO login_info VALUES {}"""
            val = (UserName,Password)
            cur.execute(sql.format(val))
            conn.commit()
            conn.close()
            self.ErorLabel.setText("Kayıt İslemi Basarılı ")


#--------------------------------------------------------------------
#                 - Add Personal  Screen  Settings -
#--------------------------------------------------------------------


class PersonelAdd(QDialog):
    def __init__(self):
        super(PersonelAdd, self).__init__()
        loadUi(AddPersonelScreenPath,self)
        self.logologin.setPixmap(QPixmap(LogoImagePath))
        self.Succes.setPixmap(QPixmap("Images/done.png"))
        self.Succes.setVisible(False)
        self.back.clicked.connect(self.GoToAdminPanel)
        self.SavePerson.clicked.connect(self.SaveNewPerson)
        self.OpenCam.clicked.connect(self.OpenCameraForPhoto)

        rakam = QRegExpValidator(QRegExp(r'[0-9]{1,11}$'))
        harf = QRegExpValidator(QRegExp('^[ A-Za-z]{1,50}$'))
        self.name.setValidator(harf)
        self.surname.setValidator(harf)
        self.tc.setValidator(rakam)
        self.tel.setValidator(rakam)



    def GoToAdminPanel(self):
        login = SetScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def PersonelAddFunc(self):
        login = PersonelAdd()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    ###################### Foto Cekme Yeri ############################

    def OpenCameraForPhoto(self):
        self.face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        ################Kullanıcı Klasörü Kontrolü#####################

        if (self.name.text() != "" and self.surname.text() != ""):
            if os.path.exists("PersonList/" + self.name.text() + " " + self.surname.text()):
                self.ErorText.setText("Kullanıcı  Kayıtlı")
            else:
                os.mkdir("PersonList/" + self.name.text() + " " + self.surname.text())

                ################Kullanıcı Fotoğrafı Kaydetme#####################

                def face_extractor(img):
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = self.face_classifier.detectMultiScale(gray, 1.3, 5)
                    if faces is ():
                        return None
                    for (x, y, w, h) in faces:
                        cropped_faces = img[y:y + h, x:x + w]

                    return cropped_faces

                cap = cv2.VideoCapture(0)
                count = 0

                while True:
                    ret, frame = cap.read()
                    if face_extractor(frame) is not None:
                        count += 1
                        face = cv2.resize(face_extractor(frame), (200, 200))
                        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                        file_name_path = 'PersonList/' + self.name.text() + " " + self.surname.text() + "/" + self.name.text() + str(
                            count) + '.jpg'

                        cv2.imwrite(file_name_path, face)
                        time.sleep(1)
                        self.profile.setPixmap(QPixmap(file_name_path))
                    else:
                        self.ErorText.setText("Yüz Bulunmadı")
                        pass
                    if cv2.waitKey(1) == 13 or count == 10:
                        break
                cap.release()
                self.ErorText.setText("Fotograf cekme islemi tamamlandı")
        else:
            self.ErorText.setText("Lütfen Önce Kişisel Bilgilerinizi Giriniz")

    ################################## Kullanıcı Kaydet Butonu ##################################
    def SaveNewPerson(self):

        Name       = self.name.text()
        Surname    = self.surname.text()
        Tc         = self.tc.text()
        Time       = self.time.dateTime().toString(self.time.displayFormat())
        BirthDate  = self.date.dateTime().toString(self.date.displayFormat())
        Gender     = self.gender.currentText()
        Depertmant = self.depertmant.text()
        TelNo      = self.tel.text()
        if Name == "" or Surname == "" or Tc =="" or Gender== "" or Depertmant == "" or TelNo == "":
            self.ErorText.setText("Lütfen Sizden İsetenilen Bütün Alanları Doldurunuz ")
        else:
            kullanici = {}

            scanner = os.scandir("PersonList")
            for file in scanner:
                document = os.scandir(file)
                liste = []
                for photo in document:
                    imagelocation = "PersonList/" + file.name + "/" + photo.name
                    testImage = face_recognition.load_image_file(imagelocation)
                    faceLocations = face_recognition.face_locations(testImage)
                    faceEncodings = face_recognition.face_encodings(testImage, faceLocations)
                    if (len(faceEncodings) != 0):
                        liste.append(faceEncodings[0])
                        print(photo.name)
                kullanici[file.name] = liste
                file = open('encoding_data.pkl', 'rb')  # Önceki kayıtları al
                veriler = pickle.load(file)
                veriler[file.name] = kullanici[file.name]
                file.close()
                file = open('encoding_data.pkl', 'wb')
                pickle.dump(veriler, file)
                file.close()
            self.Succes.setVisible(True)
            self.ErorText.setText("Kullanıcı Kaydedildi")


#--------------------------------------------------------------------
#                 - Add Camera  Screen  Settings -
#--------------------------------------------------------------------


class CameraAdd(QDialog):
    def __init__(self):
        super(CameraAdd, self).__init__()
        loadUi(AddCameraScreenPath,self)
        self.logo.setPixmap(QPixmap(LogoImagePath))
        self.back.clicked.connect(self.GoToAdminPanel)
        self.SaveCamera.clicked.connect(self.SaveCameraDatabese)

    def GoToAdminPanel(self):
        login = SetScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def AddCamera(self):
        login = CameraAdd()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def SaveCameraDatabese(self):
        UserName     = self.UserName.text()
        Pasword      = self.Pasword.text()
        IpNumber     = self. IpNumber.text()
        NameOfCAmera = self.NameOfCamera.text()
        ProtocolName = self.ProtocolName.text()
        Extention    = self.Extention.text()

        name_List = []
        adress_List = []
        file = open('cameras.pkl', 'rb')  # Önceki kayıtları al
        datas = pickle.load(file)
        file.close()
        for data in datas:  # Önceki kayırları listeye al
            name_List.append(data)
            adress_List.append(datas[data])
        name = NameOfCAmera
        if (UserName!="" and Pasword!=""):
            adress = ProtocolName + UserName + ":" + Pasword + "@" + IpNumber + "/" + Extention
        else :
            adress = ProtocolName + IpNumber + "/" + Extention
        name_List.append(name)
        adress_List.append(adress)

        data = {}
        for i in range(0, len(name_List)):  # Son listeyi kaydet
            data[name_List[i]] = adress_List[i]
        file = open('cameras.pkl', 'wb')

        pickle.dump(data, file)
        file.close()
        self.label.setText("Kamera Başarıyla Kaydedildi")


#--------------------------------------------------------------------
#               - Report Set Screen  PArametres -
#--------------------------------------------------------------------


class SetReport(QDialog):
    def __init__(self):
        super(SetReport, self).__init__()
        loadUi(ReportSetScreenPath,self)
        self.logo.setPixmap(QPixmap(LogoImagePath))
        self.back.clicked.connect(self.GoToAdminPanel)
        self.SaveMail.clicked.connect(self.SaveEmailDatabase)

        self.tableWidget.setColumnWidth(0, 244)
        self.tableWidget.setColumnWidth(1, 235)
        self.tableWidget.setColumnWidth(2, 235)

        text_file = open("Logfile.log", "r")
        logs = text_file.readlines()
        text_file.close()

        for i in range(len(logs)):
            bol = logs[i].split('-')
            self.tableWidget.setRowCount(len(logs))
            self.tableWidget.setItem(i, 0, QTableWidgetItem(bol[3]))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(bol[0]))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(bol[1]))


    def SaveEmailDatabase(self):
        """
        This Function Include  Will Save Database Email Adress

        """
        Email = self.Email.text()
        if Email== "":
            print("Lütfen Email Adresini Dogru Bir Bicimde Yazınız.  ")

        else:
            print ("kayıt basarılı ")




    def GoToAdminPanel(self):
        login = SetScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def SettingReport(self):
        login = SetReport()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)


#--------------------------------------------------------------------
#                - Perfomans Watch Screen  Settings -
#--------------------------------------------------------------------


class PerformWatch(QDialog):
    def __init__(self):
        super( PerformWatch, self).__init__()
        loadUi(PerformansWatchScreenPath,self)
        self.logo.setPixmap(QPixmap(LogoImagePath))
        self.back.clicked.connect(self.GoToAdminPanel)

    def GoToAdminPanel(self):
        login = SetScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)


#--------------------------------------------------------------------
#                - Delete Camera Screen Settings -
#--------------------------------------------------------------------


class DeleteCamera(QDialog):
    def __init__(self):
        super( DeleteCamera, self).__init__()
        loadUi(DeleteCameraScreenPath,self)
        widget.setFixedSize(1041,591)
        self.logo.setPixmap(QPixmap(LogoImagePath))
        self.back.clicked.connect(self.GoToAdminPanel)
        self.DeleteButton.clicked.connect(self.GoToDeleteBtn)


        file = open('cameras.pkl', 'rb')  # Kamera kayıtlarını al
        self.cameras = pickle.load(file)
        file.close()

        self.camera_Name_List = []
        self.camera_Adress_List = []
        i = 0
        for camera in self.cameras:  # Kamera kayıtlarını listeye kaydet
            self.camera_Name_List.append(camera)
            self.camera_Adress_List.append(self.cameras[camera])
            self.comboBox.addItem(self.camera_Name_List[i])
            i += 1


    def GoToDeleteBtn(self):
        self.index = self.camera_Name_List.index(self.comboBox.currentText())
        self.kamera = self.camera_Adress_List[self.index]


        data = {}
        for i in range(0, len(self.camera_Name_List)):  # Son listeyi kaydet
            data[self.camera_Name_List[i]] = self.camera_Adress_List[i]

        data.pop(self.comboBox.currentText())
        print(data)
        file = open('cameras.pkl', 'wb')

        pickle.dump(data, file)
        file.close()
        self.comboBox.removeItem(self.index)
        self.StateLabel.setText("Kamera Başarıyla Silindi")



    def GoToAdminPanel(self):
        login = SetScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)


#--------------------------------------------------------------------
#                - Personel Delete Screen Settings -
#--------------------------------------------------------------------


class PersonelDelete(QDialog):
    def __init__(self):
        super( PersonelDelete, self).__init__()
        loadUi(DeletePersonelScreenPath,self)
        self.logo.setPixmap(QPixmap(LogoImagePath))
        self.back.clicked.connect(self.GoToAdminPanel)
        self.DeleteButton.clicked.connect(self.GoToDeleteBtn)


    def GoToDeleteBtn(self):
        import shutil
        from imutils import paths

        name=self.name.text()
        surname=self.surname.text()

        if os.path.exists("PersonList/"+name+" "+surname):
            shutil.rmtree("PersonList/"+name+" "+surname)

            imagePaths = list(paths.list_images('PersonList'))
            knownEncodings = []
            knownNames = []
            for (i, imagePath) in enumerate(imagePaths):
                name = imagePath.split(os.path.sep)[-2]
                image = cv2.imread(imagePath)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(rgb, model='hog')
                encodings = face_recognition.face_encodings(rgb, boxes)
                for encoding in encodings:
                    knownEncodings.append(encoding)
                    knownNames.append(name)
            data = {"encodings": knownEncodings, "names": knownNames}
            f = open("face_enc", "wb")
            f.write(pickle.dumps(data))
            f.close()
            self.StateLabel.setText("Kullanıcı  Silindi")
        else:
            self.StateLabel.setText("Kullanıcı  Yok")

    def GoToAdminPanel(self):
        login = SetScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)


# main
app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)

widget.setFixedHeight(990)
widget.setFixedWidth(1670)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")


from deepface import DeepFace

demography = DeepFace.analyze("img4.jpg")

print("Yaş: ", demography["age"])
print("Cinsiyet: ", demography["gender"])
print("Duygu: ", demography["dominant_emotion"])
print("Irk/etnisite: ", demography["dominant_race"])
