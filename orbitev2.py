# -*- coding: utf-8 -*-
"""
Created on Tue May 19 01:03:47 2020

@author: Jeremy La Porte

Release 3.0
Plot object with gravitational force
"""

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
import random

    
class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setGeometry(50,50,1850,950)
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        class obj:
            def __init__(self,mass,r,vx,vy,x,y):
                self.mass = mass
                self.r = r
                self.vx,self.vy = vx,vy
                self.x,self.y = x,y
                self.POS = []
                self.col = False
                
        self.width,self.high = 1800,925 #1400,800
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(10,10,self.width,self.high))
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        # self.graphicsView.setRenderHint(QtGui.QPainter.Antialiasing)
        # self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        font = QtGui.QFont('SansSerif', 12)
        font.setBold(True)
        self.FPS = QtWidgets.QLabel(self.centralwidget)
        self.FPS.setGeometry(QtCore.QRect(20,20, 161, 50))
        self.FPS.setFont(font)
        self.DEMO = '10_stars'
        
        if self.DEMO == 'solar':
            self.OBJ = [obj(10999*10**10, 25, 0,0,1000,450),obj(10*10**10,8,3.5,0,1000,775),
                    obj(0.011*10**10, 3,3,0.1,1000,790)]
        if self.DEMO == 'real':
            self.OBJ = [obj(2/3*10**30, 25, 0,0,1000,450),obj(2*10**24,8,3.5,0,1000,775),
                    obj(7/3*10**22/2, 3,3,0.1,1000,790)]
        if self.DEMO == '10_stars':
            self.OBJ = []
            nb_etoies = 1000
            OBJappend = self.OBJ.append
            for i in range(nb_etoies):
                i,j = np.random.uniform(450,1250),np.random.uniform(75,850)
                score = (i-900)**2 + (j-450)**2
                if score <= 100000 and score >= 1000:
                    alpha  = math.atan2(i-900,j-450)
                    vx = np.sin(alpha- np.pi*0.5)*np.sqrt(score)/25
                    vy = np.cos(alpha- np.pi*0.5)*np.sqrt(score)/25
                    mass = np.random.uniform(1*10**37,10*50**37)/(2*score)
                    OBJappend(obj(mass,3,vx,vy,i,j))#np.random.uniform(2*11**17/(score+1),7*11**18/(score+1)
            print(len(self.OBJ))
            
        self.T,self.n = 200,200
        a_l = 9.461*10**15
        self.scale = 0.01*a_l/900
        self.color = False
        self.h = self.T/self.n
        self.show()
        self.Simulation()
       
   
    def getDistance(self,obj_main,obj_sec):
            return np.sqrt((obj_sec.x-obj_main.x)**2+(obj_sec.y-obj_main.y)**2)*self.scale
    # @jit(target ="cuda")
    def getPos(self,obj_main):
        atan = math.atan2
        cos = np.cos
        sin = np.sin
        vx,vy = obj_main.vx,obj_main.vy 
        x,y = obj_main.x,obj_main.y 
        acc_fx,acc_fy = 0,0
        for obj_sec in self.OBJ:
            r =  self.getDistance(obj_main,obj_sec)
            if obj_main == obj_sec:
                continue
            alpha  = atan( obj_sec.y-obj_main.y, obj_sec.x-obj_main.x )
            
            acc = 6.674*10**-11*obj_sec.mass/(r*r)
            if abs(acc) > 0.5:
                acc = acc/acc*0.5
                
            acc_x = acc*cos(alpha)
            acc_y = acc*sin(alpha)
            acc_fx += acc_x#/len(self.OBJ)
            acc_fy += acc_y#/len(self.OBJ)
        # print(acc_fx,acc_fy)
        vx += acc_fx*self.h
        vy += acc_fy*self.h
            
        y += vy*self.h
        x += vx*self.h
        
        # if self.DEMO == 'solar':
        #     if len(obj_main.POS) >=800:
        #         obj_main.POS = obj_main.POS[2:]
        #     obj_main.POS.append(obj_main.x)
        #     obj_main.POS.append(obj_main.y)

    def outOfScreen(self,obj):
        return obj.x < 25-obj.r*0.5 or obj.x > self.width-50 +obj.r*0.5 or obj.y < 25-obj.r*0.5 or obj.y > self.high -50+obj.r*0.5
        
    def Draw(self):
        self.SDraw_Time = time.perf_counter()
        self.scene.clear()
        Max = 5
        self.scene.addRect(25,25,self.width-50,self.high -50,brush = QtGui.QBrush(QtGui.QColor(0,0,0)))#rectangle de simulation
        addPoint = self.scene.addEllipse
        for obj in self.OBJ:
            if not self.outOfScreen(obj):
                self.SPose_Time = time.perf_counter()
                self.getPos(obj)
                self.Pose_Time = time.perf_counter()
                V = np.sqrt(obj.vx*obj.vx +obj.vy*obj.vy)
                if V > Max:
                    Max = V
                if self.color:
                    
                    if V <= Max/2:
                        Color = QtGui.QColor(0,(255*2/Max)*V,255)#(255*2/Max)*V,255,0
                        Color_p = ((255*2/Max)*V,255,0)
                        
                    else:
                        Color = QtGui.QColor((255*2/Max)*(V-Max/2),255,255)#QtGui.QColor(255,255-(255*2/Max)*(V-Max/2),0)
                        Color_p = (255,255-(255*2/Max)*(V-Max/2),0)
                    
                    addPoint(obj.x-obj.r,obj.y-obj.r,obj.r*2,obj.r*2,brush = QtGui.QBrush(Color))
                else:
                    addPoint(obj.x-obj.r,obj.y-obj.r,obj.r*2,obj.r*2, 
                                              brush = QtGui.QBrush(QtGui.QColor(V*255/Max,255,255)))
                

                for coord in range(0,len(obj.POS),2):
                    self.scene.addLine(obj.POS[coord],obj.POS[coord+1],obj.POS[coord],
                                        obj.POS[coord+1],QtGui.QPen(QtGui.QColor(0,obj.r*8,obj.r*8),2))
        self.Draw_Time = time.perf_counter()
        
    
    def Simulation(self):
        start_time = time.perf_counter()
        for Iteration in range(self.n):
            
            start_iter = time.perf_counter()
            self.Draw()
            
            self.exportAsPng('galaxy_png_'+str(Iteration)+'.png') 
            temps_iter = time.perf_counter()
            print(f'Image:{Iteration}({round(Iteration*100/self.n,1)} %)','  Temps:',
                  round((temps_iter-start_iter)*1000,2),'ms',
                  'D',round((self.Draw_Time-self.SDraw_Time)*1000,2),'ms',
                  'P',round((self.Pose_Time-self.SPose_Time)*1000,2),'ms',
                  'Png',round((self.temps_png-self.start_png)*1000,2),'ms')
            
            if Iteration == self.n-1:
                temps = round(time.perf_counter()-start_time,2)
                print(f"Finished in {temps} s")
            
    def exportAsPng(self, fileName):
        self.start_png = time.perf_counter()
        pixmap = QtGui.QPixmap(self.scene.sceneRect().size().toSize())
         
        painter = QtGui.QPainter()
        painter.begin(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.graphicsView.render(painter)
        painter.end()
         
        pixmap.save(fileName, "PNG")
        self.temps_png = time.perf_counter()
            
if __name__ == "__main__" :
    """ Show and Close the window"""
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    sys.exit(app.exec_())
