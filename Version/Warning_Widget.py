import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import threading
import qdarkstyle

class Warning_Widget(QWidget):
    Vedio_Running_Indicator = 'No'
    Vedio_Recording_Indicator = 'No'
    Vedio_Save_Path = ''
    '''每Vedio_Number帧保存一个视频'''
    Record_Vedio_Counter = int(0)
    Vedio_Number = 90000#一个小时保存一个视频
    def __init__(self, parent = None):
        super(Warning_Widget, self).__init__(parent)
        self.SetUI()

    def SetUI(self):
        self.resize(444,250)
        self.setWindowTitle('Camera Version')
        self.FixedHeight = 30
        self.Font = QFont()
        self.Font.setPixelSize(18)

        layout = QVBoxLayout()

        self.Cam_State = QLineEdit()
        self.Cam_State.setEnabled(False)
        self.Cam_State.setFont(self.Font)

        self.NumOfObs = QLineEdit()
        self.NumOfObs.setEnabled(False)
        self.NumOfObs.setFont(self.Font)

        self.EgoVehicle_Speed = QLineEdit()
        self.EgoVehicle_Speed.setEnabled(False)
        self.EgoVehicle_Speed.setFont(self.Font)

        layout.addWidget(self.Cam_State)
        layout.addWidget(self.NumOfObs)
        layout.addWidget(self.EgoVehicle_Speed)

        self.setLayout(layout)
        
        self.Cam_State.setText("State : --")
        self.EgoVehicle_Speed.setText("Ego Vehicle Speed : --")
        self.NumOfObs.setText("Number of Obstacle : --")

    def updateCamState(self, state):
        self.Cam_State.setText("State : " + state)

    def updateEgoSpeed(self, speed):
        self.EgoVehicle_Speed.setText("Ego Vehicle Speed : " + str(speed))

    def updateNumOfObs(self, num):
        self.NumOfObs.setText("Number of Obstacle : " + str(num))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    win = Warning_Widget()
    win.show()
    sys.exit(app.exec_())

