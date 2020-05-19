# -*- coding: utf-8 -*-
"""
Created on Tue May 19 01:03:47 2020

@author: Jeremy La Porte

Release 1.0
Plot object with gravitational force
"""

import keyboard
from PyQt5 import QtCore, QtGui, QtWidgets
import PyQt5.QtCore 
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QPen
import pyqtgraph as pg
import datetime
import sys
import time
import numpy as np
import math


    
class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setGeometry(50,50,1850,950)
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        
        # self.horizontalSlider_1 = QtWidgets.QSlider(Qt.Horizontal,self)
        # self.horizontalSlider_1.setGeometry(QtCore.QRect(100, 850, 160, 22))
        # self.horizontalSlider_1.setOrientation(QtCore.Qt.Horizontal)
        # self.horizontalSlider_1.setMaximum(100)
        # self.horizontalSlider_1.setMinimum(1)
        # self.horizontalSlider_1.valueChanged.connect(self.Draw)
        # self.label = QtGui.QLabel(str(self.horizontalSlider_1.value()),self)
        # self.label.move(120,825)
        class obj:
            def __init__(self,mass,r,vx,vy,x,y):
                self.mass = mass
                self.r = r
                self.vx,self.vy = vx,vy
                self.x,self.y = x,y
                self.POS = []
                
        self.width,self.high = 1800,925 #1400,800
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(10,10,self.width,self.high))
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setRenderHint(QtGui.QPainter.Antialiasing)
        # self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        font = QtGui.QFont('SansSerif', 12)
        font.setBold(True)
        self.FPS = QtWidgets.QLabel(self.centralwidget)
        self.FPS.setGeometry(QtCore.QRect(20,20, 161, 50))
        self.FPS.setFont(font)
        self.DEMO = 'solar'

        if self.DEMO == 'solar':
            self.OBJ = [obj(10999*10**10, 25, 0,0,1000,450),obj(10*10**10,8,3.5,0,1000,775),
                    obj(0.011*10**10, 3,3,0.1,1000,790)]
        if self.DEMO == '10_stars':
            self.OBJ = [obj(1000*10**10, 25, 0,0,1000,450)]
            for i in range(50,1800,100):
                for j in range(50,850,100):
                    self.OBJ.append(obj(0.01*10**10,5,0,0,i,j))
            
            
        self.G = 6.674*10**-11
        self.dt = 15
        self.cond = False
        self.timer3 = pg.QtCore.QTimer()
        self.timer3.timeout.connect(self.Draw)
        self.timer3.start(self.dt) # refresh rate in ms
        
        self.show()
   

    def getDistance(self,obj_main,obj_sec):
            return np.sqrt((obj_sec.x-obj_main.x)**2+(obj_sec.y-obj_main.y)**2)

    def getPos(self,obj_main):
        # start_time = time.time()
            
        self.OBJ_2 = self.OBJ
        index = self.OBJ_2.index(obj_main)
        self.OBJ_2.remove(obj_main)
        
            
        for obj_sec in self.OBJ:
            # print(self.OBJ.index(obj_sec))
            alpha  = math.atan2( obj_sec.y-obj_main.y, obj_sec.x-obj_main.x )
            r =  self.getDistance(obj_main,obj_sec)
            
            acc = self.G*obj_sec.mass/r**2
            
            obj_main.vx += np.cos(alpha)*acc 
            obj_main.vy += np.sin(alpha)*acc
            
            obj_main.y +=  obj_main.vy
            obj_main.x += obj_main.vx

            # if self.cond:
            #     if len(obj_main.POS) >=800:
            #         obj_main.POS = obj_main.POS[2:]
            #     obj_main.POS.append(obj_main.x)
            #     obj_main.POS.append(obj_main.y)
            # self.cond = not(self.cond)

        self.OBJ_2.insert(index,obj_main)
        # print((time.time()-start_time)*1000)

    def outOfScreen(self,obj):
        # print(obj.x,obj.y)
        return obj.x < 25-obj.r/2 or obj.x > self.width-50 +obj.r/2 or obj.y < 25-obj.r/2 or obj.y > self.high -50+obj.r/2
        
    def Draw(self):
        start_time = time.time()
        self.scene.clear()
        self.scene.addRect(25,25,self.width-50,self.high -50,brush = QtGui.QBrush(QtGui.QColor(200,200,200)))
        
        for obj in self.OBJ:
            # print(obj.x,obj.y)
            # self.scene.addRect(0,0,1200,800,brush = QtGui.QBrush(QtGui.QColor(255,255,255)))
            # print(obj.x,obj.y)
            
            # self.scene.addRect(0,0,15,15,brush = QtGui.QBrush(QtGui.QColor(255,255,255)))
            # self.scene.addRect(0,800,-15,-15,brush = QtGui.QBrush(QtGui.QColor(255,255,0)))
            # self.scene.addRect(1200,0,15,15,brush = QtGui.QBrush(QtGui.QColor(255,255,0)))
            
            if not self.outOfScreen(obj):
                self.getPos(obj)
                self.scene.addEllipse(obj.x-obj.r,obj.y-obj.r,obj.r*2,obj.r*2, brush = QtGui.QBrush(QtGui.QColor(0,obj.r*8,obj.r*8)))
                # for coord in range(0,len(obj.POS),2): 
                #     self.scene.addLine(obj.POS[coord],obj.POS[coord+1],obj.POS[coord],
                #                         obj.POS[coord+1],QtGui.QPen(QtGui.QColor(0,obj.r*8,obj.r*8),2))
            # else:
                # print("out of screen")

        temps_simu = (time.time()-start_time)*1000
        print(temps_simu)
        if temps_simu >= self.dt:
            self.FPS.setText(str(int(1000/temps_simu))+ 'FPS')
            print(temps_simu)
            
if __name__ == "__main__" :
    """ Show and Close the window"""
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    sys.exit(app.exec_())