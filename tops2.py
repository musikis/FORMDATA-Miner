# -*- coding: utf-8 -*- 

import sys
import os
import re

import tkinter
from contextlib import suppress
from math import sin,pi
from PySide6.QtCore import Qt
from PySide6 import QtXml, QtUiTools, QtGui
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidget, QMessageBox,  QHeaderView, QTableWidgetItem, QListWidgetItem
import matplotlib.pyplot as plt
#import matplotlib
#matplotlib.use('TkAgg')
#import matplotlib.pyplot as plt
from configparser import ConfigParser, ExtendedInterpolation

#메인 윈도우 클래스
class MainView(QMainWindow):    
    def __init__(self):
        super().__init__()
        self.setupUI()

    #UI 셋업
    def setupUI(self):

        global UI_set
        global msgBox
        
        UI_set = QtUiTools.QUiLoader().load(resource_path('top.ui'))
        msgBox = QMessageBox()
        
        self.setCentralWidget(UI_set)
        self.setWindowTitle("TOP Foil 데이터 수집기")
        self.setWindowIcon(QtGui.QIcon(resource_path('top.ico')))
        self.resize(1024,768)
        self.show()
        self.table=UI_set.tableWidget

        UI_set.pushButton.clicked.connect(self.getFileNames) #파일 열기
        UI_set.pushButton_2.clicked.connect(self.mainFrame) #실행
        UI_set.pushButton_3.clicked.connect(self.exitPrg) #나가기
        UI_set.pushButton_4.clicked.connect(self.makeGraph) #그래프
        UI_set.pushButton_5.toggled.connect(self.toggler) #소재두께
        
        copyShortcut = QShortcut(QKeySequence.Copy,self) #클립보드
        copyShortcut.activated.connect(self.copy)
    #소재두께
    def toggler(self,state):
        global addT
        addT='%d'%({True: 1, False: 0}[state])
        if not state : addT=0
        
                
        if not fileNames[0]: return 
        else : self.mainFrame()
        
        return addT
        
        
    #클립보드
    def copy(self):
        selectedRangeList = self.table.selectedRanges()
        if selectedRangeList == [] :
            return

        text = ""
        selectedRange = selectedRangeList[0]
        for i in range(selectedRange.rowCount()):
            if i > 0:
                text += "\n"
            for j in range(selectedRange.columnCount()):
                if j > 0:
                    text += "\t"
                itemA = self.table.item(selectedRange.topRow()+i,selectedRange.leftColumn()+j)
                if itemA :
                    text += itemA.text()
        text += '\n'

        QApplication.clipboard().setText(text)    

#그래프
    def makeGraph(self):
        #self.mainFrame()
        global isThrust
        
        
        cul=0
        if not fileNames[0]:
            mbxalt("파일을 선택하지 않으셨습니다.")
            return
        
        plt.figure(1,[13,4])
        
        if isThrust==0:
            #addThickness=float(addT)*topThickness
            USL = [number+addThickness for number in topUpper]
            LSL = [number+addThickness for number in topLower]
            plt.plot(plotDataX[cul][0:13],USL,'--o')
            plt.plot(plotDataX[cul][0:13],LSL,'--o')
            plt.fill_between(plotDataX[cul][0:13], USL, LSL, color='greenyellow', alpha=0.5)
            for openFile in fileNames[0]:
                plt.plot(plotDataX[cul],plotDataY[cul],label=os.path.basename(openFile))
                cul+=1
        else:
            #addThickness=float(addT)*thrustThickness
            USL = [number+addThickness for number in thrustUpper]
            LSL = [number+addThickness for number in thrustLower]
            plt.plot(plotDataX[cul][0:4],USL,'--o')
            plt.plot(plotDataX[cul][0:4],LSL,'--o')
            plt.fill_between(plotDataX[cul][0:4], USL, LSL, color='greenyellow', alpha=0.5)
            for openFile in fileNames[0]:
                plt.plot(plotDataX[cul][0:4],plotDataY[cul][0:4],'-o',label=os.path.basename(openFile))
                cul+=1
        
        plt.xlabel("X")
        plt.ylabel("Z")
        plt.legend(loc='upper left')
        
        plt.show()             

    #파일열기
    def getFileNames(self):
        global fileNames
        global exelLocation
        
        itemA = QListWidgetItem()
        fileNames=QFileDialog.getOpenFileNames(self, self.tr("Open Data files"), exelLocation, self.tr("Data Files (*.txt)"))
                
        if not fileNames[0]:
            mbxalt("파일을 선택하지 않으셨습니다.")
            return
            
        for openFile in fileNames[0]:
            itemA.setText(openFile)
            UI_set.listWidget_2.addItem(itemA)
        
        exelLocation=os.path.dirname(fileNames[0][0])
        configure('GENERAL','location',exelLocation)
                
    #실행            
    def mainFrame(self):
        global isThrust
        global addThickness
        global addT
                      
        if not fileNames[0]:
            mbxalt("파일을 선택하지 않으셨습니다.")
            return
        
        b=0 
        
        bss=len(fileNames[0])
   
        a=open(fileNames[0][0],'r',encoding = 'cp949')
        lines=a.readlines()
               
        for word in lines:
            if '(X)' in word : b+=1

        if not b : 
            
            addThickness=float(addT)*thrustThickness
            n,b,bss=thrust(bss,addThickness)
            widget(b,bss,1)
            UI_set.tableWidget.setVerticalHeaderLabels(n)
            isThrust=1
            return

        #plotDataX=[[0 for col in range (b)] for row in range(bss)]
        #plotDataY=[[0 for col in range (b)] for row in range(bss)]
        addThickness=float(addT)*topThickness
        
        
        n=topfoil(b,bss,addThickness)

        widget(b,bss,0)
        

        UI_set.tableWidget.setVerticalHeaderLabels(n)             
        isThrust=0

    def exitPrg(self):
        
        result=mbxqa("종료하시겠습니까")

        if result == QMessageBox.Yes:
            sys.exit()

        elif result == QMessageBox.No:
            pass

def widget(b,a,c):
    UI_set.tableWidget.setColumnCount(b)
    
    UI_set.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    UI_set.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
    if c==0:
        UI_set.tableWidget.setRowCount(a*2)
        for i in range(0,a):
            for j in range (0,b):
                UI_set.tableWidget.setItem(i*2, j, QTableWidgetItem(str('%.4f'%plotDataX[i][j])))
                UI_set.tableWidget.setItem(i*2+1, j , QTableWidgetItem(str('%4f'%plotDataY[i][j])))
    else:
        UI_set.tableWidget.setRowCount(a)
        for i in range(0,a):
            for j in range (0,b):
                UI_set.tableWidget.setItem(i, j, QTableWidgetItem(str('%.4f'%plotDataY[i][j])))


def topfoil(b,bss,thickness):
    
    global plotDataX
    global plotDataY
    cul=0
    n=list()
    plotDataX=[[0 for col in range (b)] for row in range(bss)]
    plotDataY=[[0 for col in range (b)] for row in range(bss)]
    
    for openFile in fileNames[0]:
        a=open(openFile,'r',encoding = 'cp949')
        lines=a.readlines()
                        
        plotDataX[cul]=floater(finder('(X)',lines),0,0)
        plotDataY[cul]=floater(finder('(Z)',lines),1,thickness)

        n.append('%s X'%os.path.basename(openFile))
        n.append('%s Y'%os.path.basename(openFile))
                 
        cul+=1
   
    return n
    
def thrust(bss,thickness):
    global plotDataX
    global plotDataY
    global fileNames
    b=0
    cul=0
    n=list()
        
    for openFile in fileNames[0]:
        a=open(openFile,'r',encoding = 'cp949')
        lines=a.readlines()


    for word in lines:
        if '중심거리' in word : b+=1
    
    plotDataX=[[0 for col in range (b)] for row in range(bss)]
    plotDataY=[[0 for col in range (b)] for row in range(bss)]
    for openFile in fileNames[0]:
        a=open(openFile,'r',encoding = 'cp949')
        lines=a.readlines()
        plotDataY[cul]=floater(finder('중심거리',lines),2,thickness)
        for i in range(0,b):
            plotDataX[cul][i]=(float(i+1))
        
        n.append('%s Y'%os.path.basename(openFile))
                     
        cul+=1

    return n,b,bss

def mbxalt(a):
    msgBox.setWindowTitle("Alert Window") # 메세지창의 상단 제목
    msgBox.setWindowIcon(QtGui.QPixmap(resource_path('top.ico'))) # 메세지창의 상단 icon 설정
    msgBox.setIcon(QMessageBox.Information) # 메세지창 내부에 표시될 아이콘
    msgBox.setStandardButtons(QMessageBox.Ok) # 메세지창의 버튼
    msgBox.setInformativeText(a) # 메세지 내용
    msgBox.exec_()

def mbxqa(a):
    msgBox.setWindowTitle("Alert Window") # 메세지창의 상단 제목
    msgBox.setWindowIcon(QtGui.QPixmap(resource_path('top.ico'))) # 메세지창의 상단 icon 설정
    msgBox.setIcon(QMessageBox.Information) # 메세지창 내부에 표시될 아이콘
    msgBox.setInformativeText(a) # 메세지 내용
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No) # 메세지창의 버튼
    msgBox.setDefaultButton(QMessageBox.Yes) # 포커스가 지정된 기본 버튼
    result = msgBox.exec_()
    return result

def finder(a,b):
	c=list()
	for word in b:
		if a in word:
			c.append(word)
	return c

def floater(a,n,thickness):
    
    i=0
    b=list()
    if n==0:
        b=list(map(lambda s: float(s.strip().strip('좌표차(XZ)mm').strip('중심거리')),a))
    elif n==1:
        b=list(map(lambda s: float(s.strip().strip('좌표차(XZ)mm'))+thickness,a))
        
    elif n==2:
        for add in a:
            i+=1
            if i<5:
                b.append(float(add.strip().strip('중심거리mm'))+thickness)
        
            else:b.append(float(add.strip().strip('중심거리mm'))*float(sin(pi/3)))
    #b=list(map(lambda s: float(re.search("\d+\.\d+",s).group()), a))
    return b

#파일 경로

#pyinstaller로 원파일로 압축할때 경로 필요함
def resource_path(relative_path):

    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.abspath('.'), relative_path)

def configure(a,b,c):
    if not config.has_section(a):
        config.add_section(a)
    config.set(a,b,c)
    configFile = open("config.ini", "w")
    config.write(configFile)
    configFile.close()

def getConfig(a,b,c):
    try : 
        d=config.get(a,b)
        return d
    except : 
        configure(a, b, c)
        return c

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('config.ini')
plotDataX=list()        
plotDataY=list()
fileNames=list([''])
addThickness=0
isThrust=0
addT=0

thrustUpper=list(map(float,getConfig('THRUSTBUMP','thrust_upper','0.411, 0.421, 0.431, 0.431').split(',')))
thrustLower=list(map(float,getConfig('THRUSTBUMP','thrust_lower','0.371, 0.381, 0.391, 0.391').split(',')))
topThickness=float(getConfig('TOPFOIL', 'top_thickness','0.203'))
topUpper=list(map(float,getConfig('TOPFOIL','top_upper','0.0400, 0.1503, 0.2537, 0.3475, 0.4320, 0.5038, 0.5658, 0.6133, 0.6434, 0.6640, 0.6738, 0.6779, 0.6752, 0.6748, 0.6732').split(',')))
topLower=list(map(float,getConfig('TOPFOIL','top_lower','0.0000, 0.0500, 0.0900, 0.1175, 0.1374, 0.1416, 0.1365, 0.1201, 0.0902, 0.0424, -0.0198, -0.0905, -0.1725, -0.2148, -0.3246').split(',')))
thrustThickness=float(getConfig('THRUSTBUMP', 'thrust_thickness','0.089'))
exelLocation=getConfig('GENERAL','location',os.getcwd())


if __name__ == '__main__':

    app = QApplication(sys.argv)
    main = MainView()
    #main.show()
    sys.exit(app.exec_())
