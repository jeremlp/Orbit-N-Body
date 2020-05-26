# -*- coding: utf-8 -*-
"""
Created on Tue May 19 01:03:47 2020

@author: Jeremy La Porte

Release 2.0
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
import random
from numba import jit, cuda

    
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
        self.DEMO = 'solar'

        if self.DEMO == 'solar':
            self.OBJ = [obj(10999*10**10, 25, 0,0,1000,450),obj(10*10**10,8,3.5,0,1000,775)]
        if self.DEMO == 'real':
            self.OBJ = [obj(2/3*10**30, 25, 0,0,1000,450),obj(2*10**24,8,3.5,0,1000,775),
                    obj(7/3*10**22/2, 3,3,0.1,1000,790)]
        if self.DEMO == '10_stars':
            self.OBJ = []
            nb_etoies = 80
            for i in range(350,1500,nb_etoies):
                for j in range(50,850,nb_etoies):
                    score = (i-800)**2 + (j-450)**2
                    if score <= 100000:
                        alpha  = math.atan2(i-800,j-450)
                        vx = np.sin(alpha- np.pi*0.5)*np.sqrt(score)/100
                        vy = np.cos(alpha- np.pi*0.5)*np.sqrt(score)/100
                        self.OBJ.append(obj(np.random.uniform(4*11**12,6*11**13),2,vx,vy,i,j))
            print(len(self.OBJ))
            
        self.G = 6.674*10**-11
        self.T,self.n = 200,5
        self.color = False
        self.h = self.T/self.n
        self.show()
        self.Simulation()
       
   

    def getDistance(self,obj_main,obj_sec):
            return np.sqrt((obj_sec.x-obj_main.x)**2+(obj_sec.y-obj_main.y)**2)
    # @jit(target ="cuda")
    def getPos(self,obj_main):
        # start_time = time.time()
        # self.OBJ_2 = self.OBJ
        index = self.OBJ.index(obj_main)
        # self.OBJ.remove(obj_main)
        L = self.OBJ[0:index]+self.OBJ[index+1:]
        acc_fx,acc_fy = 0,0
        for obj_sec in L:
            r =  self.getDistance(obj_main,obj_sec)
            if abs(r) >= 400 :
                continue
            alpha  = math.atan2( obj_sec.y-obj_main.y, obj_sec.x-obj_main.x )
            
            acc = self.G*obj_sec.mass/r**2
            if abs(acc) > 0.5:
                acc = acc/acc*0.5
            acc_x = acc*np.cos(alpha)
            acc_y = acc*np.sin(alpha)
            acc_fx += acc_x#/len(self.OBJ)
            acc_fy +=acc_y#/len(self.OBJ)
        # print(acc_fx,acc_fy)
        obj_main.vx += acc_fx*self.h
        obj_main.vy += acc_fy*self.h
            
        obj_main.y += obj_main.vy*self.h
        obj_main.x += obj_main.vx*self.h
        
        if self.DEMO == 'solar':
            if len(obj_main.POS) >=800:
                obj_main.POS = obj_main.POS[2:]
            obj_main.POS.append(obj_main.x)
            obj_main.POS.append(obj_main.y)

    def outOfScreen(self,obj):
        return obj.x < 25-obj.r*0.5 or obj.x > self.width-50 +obj.r*0.5 or obj.y < 25-obj.r*0.5 or obj.y > self.high -50+obj.r*0.5
        
    def Draw(self):
        
        self.scene.clear()

        self.scene.addRect(25,25,self.width-50,self.high -50,brush = QtGui.QBrush(QtGui.QColor(200,200,200)))#rectangle de simulation
        for obj in self.OBJ:
            if not self.outOfScreen(obj):
                self.save_time = time.perf_counter()
                self.getPos(obj)
                print(round(obj.x,3),round(obj.y,3))
                V = np.sqrt(obj.vx*obj.vx +obj.vy*obj.vy)
                if self.color:
                    if V <= 4.6:
                        self.scene.addEllipse(obj.x-obj.r,obj.y-obj.r,obj.r*2,obj.r*2, 
                                              brush = QtGui.QBrush(QtGui.QColor((255*2/9)*V,255,0)))
                    else:
                        self.scene.addEllipse(obj.x-obj.r,obj.y-obj.r,obj.r*2,obj.r*2, 
                                              brush = QtGui.QBrush(QtGui.QColor(255,255-(255*2/9)*(V-9/2),0)))
                else:
                    self.scene.addEllipse(obj.x-obj.r,obj.y-obj.r,obj.r*2,obj.r*2, 
                                              brush = QtGui.QBrush(QtGui.QColor(0,0,0)))
                    
                self.temps_save = time.perf_counter()
                for coord in range(0,len(obj.POS),2):
                    self.scene.addLine(obj.POS[coord],obj.POS[coord+1],obj.POS[coord],
                                        obj.POS[coord+1],QtGui.QPen(QtGui.QColor(0,obj.r*8,obj.r*8),2))
        
    
    def Simulation(self):
        start_time = time.perf_counter()
        for Iteration in range(self.n):
            
            start_iter = time.perf_counter()
            self.Draw()
            
            self.exportAsPng('galaxy_png_'+str(Iteration)+'.png') 
            temps_iter = time.perf_counter()
            print(f'Image:{Iteration}({round(Iteration*100/self.n,1)} %)','  Temps:',
                  round((temps_iter-start_iter)*1000,2),'ms',
                  round((self.temps_save-self.save_time)*1000,2),'ms',
                  round((self.temps_png-self.start_png)*1000,2),'ms')
            
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
