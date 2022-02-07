from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import sys
import qdarkstyle
from Model.CAN_DATA import *

class CAN_FigurePlot(QWidget):
    def __init__(self,parent=None):
        super(CAN_FigurePlot, self).__init__(parent)
        self.SetUI()
        '''定义三个QTimer来会绘图'''
        self.Timer_Cur_Ped = QTimer()
        self.Timer_Cur_Veh = QTimer()
        self.Timer_Cur_Lane = QTimer()
        self.Timer_Cur_Ped.timeout.connect(self.Plot_Data_Ped)
        self.Timer_Cur_Veh.timeout.connect(self.Plot_Data_Veh)
        self.Timer_Cur_Lane.timeout.connect(self.Plot_Data_Lane)
        self.Obstacle = CAN_Data_Obstacle()
        self.Lane = CAN_Data_Lane()
        self.Vehicle = CAN_Data_Vehicle

        '''不同属性的点集(人、车、车道线)用不同的曲线来绘制'''
        self.Curve_Generate()

    def SetUI(self):
        self.resize(1144,600)
        self.setWindowTitle("VERSION CAN")
        self.VB = QVBoxLayout()
        self.win = pg.GraphicsLayoutWidget()
        self.VB.addWidget(self.win)
        self.setLayout(self.VB)
        self.Picture = self.win.addPlot()
        self.Picture.setRange(xRange=[-1, 60], yRange=[-10, 10], padding=0)

    '''关闭定时器同时清除绘图界面'''
    def Timer_Stop(self):
        self.Timer_Cur_Ped.stop()
        self.Timer_Cur_Veh.stop()
        self.Timer_Cur_Lane.stop()
        self.Clear_Window()

    def Clear_Window(self):
        self.Cur_ped.clear()
        self.Cur_Veh.clear()
        for i in range(2):
            exec('self.Cur_Lane%d.clear()'%i)

    def Clear_Original(self):
        self.Cur_Original.clear()

    def Curve_Generate(self):
        '''
        这个函数如果要生成不同属性的点集，首先需要生成不同的曲线cur
        :return:
        '''
        '''Car Origin'''
        self.Cur_Original = pg.ScatterPlotItem(size=30, pen=pg.mkPen(None), brush=pg.mkBrush(250, 250, 120, 120))
        self.Picture.addItem(self.Cur_Original)
        '''Pedestrian'''
        self.Cur_ped = pg.ScatterPlotItem(size=20, pen=pg.mkPen(None), brush=pg.mkBrush(255, 0, 0, 120))
        self.Picture.addItem(self.Cur_ped)
        '''Vehicle'''
        self.Cur_Veh = pg.ScatterPlotItem(size=20, pen=pg.mkPen(None), brush=pg.mkBrush(0, 0, 255, 120))
        self.Picture.addItem(self.Cur_Veh)
        '''Lane 0->left, 1->right'''
        self.Cur_Lane0 = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(0, 255, 0, 120))
        self.Picture.addItem(self.Cur_Lane0)
        self.Cur_Lane1 = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(0, 255, 0, 120))
        self.Picture.addItem(self.Cur_Lane1)
        self.Cur_Lane2 = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(255,0, 0, 85))
        self.Picture.addItem(self.Cur_Lane2)
        self.Cur_Lane3 = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(255,0, 0, 85))
        self.Picture.addItem(self.Cur_Lane3)
        self.Cur_Lane4 = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(255,0, 0, 85))
        self.Picture.addItem(self.Cur_Lane4)
        self.Cur_Lane5 = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(255,0, 0, 85))
        self.Picture.addItem(self.Cur_Lane5)
        self.Cur_Lane6 = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(255,0, 0, 85))
        self.Picture.addItem(self.Cur_Lane6)
        self.Cur_Lane7 = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(255,0, 0, 85))
        self.Picture.addItem(self.Cur_Lane7)
        self.Cur_Lane8 = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(255,0, 0, 85))
        self.Picture.addItem(self.Cur_Lane8)
        self.Cur_Lane9 = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(255,0, 0, 85))
        self.Picture.addItem(self.Cur_Lane9)
        self.Cur_Lanes = [self.Cur_Lane0,self.Cur_Lane1,self.Cur_Lane2,self.Cur_Lane3,self.Cur_Lane4,self.Cur_Lane5,self.Cur_Lane6,self.Cur_Lane7,self.Cur_Lane8,self.Cur_Lane9]

    def Original(self):
        self.Cur_Original.setData([{'pos': [0, 0], 'data': 1}], symbolBrush=(120, 120, 120), symbolPen='w', symbol = 's')

    def Plot_Data_Ped(self):
       
        self.Cur_ped.setData([{'pos': [self.Obstacle.Ped_X[i], self.Obstacle.Ped_Y[i]], 'data': 1} for \
                              i in range(self.Obstacle.Ped_X.shape[0]) if (self.Obstacle.Ped_X[i] or self.Obstacle.Ped_Y[i])], \
                             symbolBrush=(0, 255, 0), symbolPen='w', symbol = 'o')

    def Plot_Data_Veh(self):
        self.Cur_Veh.setData([{'pos': [self.Obstacle.Veh_X[i], self.Obstacle.Veh_Y[i]], 'data': 1} for \
                              i in range(self.Obstacle.Veh_X.shape[0]) if (self.Obstacle.Veh_X[i] or self.Obstacle.Veh_Y[i])], \
                             symbolBrush=(255, 255, 0), symbolPen='y', symbol='t')

    def Plot_Data_Lane(self):
        for j in range(10):
            self.Cur_Lanes[j].setData([{'pos': [self.Lane.Lane_X[j][i], self.Lane.Lane_Y[j][i]], 'data': 1} for \
                                i in range(self.Lane.Lane_X[j][:].shape[0]) if self.Lane.Lane_Y[j][:].all()], \
                               symbolBrush=(0, 255, 0), symbolPen='b', symbol='s')
        pass
        '''self.Cur_Lane0.setData([{'pos': [self.Lane.Lane_X[0][i], self.Lane.Lane_Y[0][i]], 'data': 1} for \
                                i in range(self.Lane.Lane_X[0][:].shape[0]) if self.Lane.Lane_Y[0][:].all()], \
                               symbolBrush=(0, 255, 0), symbolPen='b', symbol='s')
        self.Cur_Lane1.setData([{'pos': [self.Lane.Lane_X[1][i], self.Lane.Lane_Y[1][i]], 'data': 1} for \
                                i in range(self.Lane.Lane_X[1][:].shape[0]) if self.Lane.Lane_Y[1][:].all()], \
                               symbolBrush=(0, 255, 0), symbolPen='b', symbol='s')'''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    Mainwindow = CAN_FigurePlot()
    Mainwindow.show()
    sys.exit(app.exec_())
