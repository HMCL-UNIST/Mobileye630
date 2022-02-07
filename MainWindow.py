from pydantic import NoneBytes
from Version.CAN_Presetting import *
from Version.CAN_Channel import *
from Version.CAN_FigurePlot import *
from Version.Warning_Widget import *
from Version.Camera_Version import *
from Model.CAN_Structure import *
from Model.CAN_Analysis import *
from Model.CAN_Parameter_Set import *
from canlib import kvadblib, canlib
from Model.CAN_Receive import *
from Model.CAN_Coordinate import *
import argparse
import threading
import csv
import time

bitrates = {
    '1M': canlib.canBITRATE_1M,
    '500K': canlib.canBITRATE_500K,
    '250K': canlib.canBITRATE_250K,
    '125K': canlib.canBITRATE_125K,
    '100K': canlib.canBITRATE_100K,
    '62K': canlib.canBITRATE_62K,
    '50K': canlib.canBITRATE_50K,
    '83K': canlib.canBITRATE_83K,
    '10K': canlib.canBITRATE_10K,
}

class MainWindows(QWidget):
    '''
    OpenCAN: CAN设备是否打开标志位，0：否，1：是；
    Thread_Msg_Ped_Rec_Indicator：CAN设备接收行人报文的线程标志位，'Stop'：线程处于关闭状态，'Start'：线程处于运行状态；
    Data_Ped_Counter：用于对行人报文的计数，判断行人识别是否在持续；
    Data_Veh_Counter：用于对车辆报文的计数，判断车辆识别是否在持续；
    Record_Data_Indicator：是否记录数据；
    '''
    OpenCAN = 'No'
    Thread_Msg_Ped_Rec_Indicator = 'Stop'
    Record_Data_Indicator = 'No'
    '''判断行人和车辆是否还存在的计数器'''
    Data_Ped_Counter = np.zeros([64, 2])
    Data_Veh_Counter = np.zeros([64, 2])
    '''每Data_Number个数据保存一个文件'''
    Record_Data_Counter = int(0)
    Data_Number = 5000 #1000000
    def __init__(self,parent=None):
        super(MainWindows,self).__init__(parent)
        '''绘制主窗口'''
        self.SetUI()
        '''定义的信号与槽'''
        self.Signal_Def()
        '''Set default values'''
        self.set_default_values()

    def SetUI(self):
        self.resize(1144,850)
        self.setWindowTitle('Mobileye Sight')
        self.setWindowIcon(QIcon('./Pic/Logo.jpg'))
        self.VB = QVBoxLayout()
        self.HB = QHBoxLayout()
        self.CAN_Channel = CAN_Channel()
        self.CAN_Presetting = CAN_Presetting()
        self.CAN_FigurePlot = CAN_FigurePlot()
        self.Camera_Version = Camera_Version()
        self.Warning_Widget = Warning_Widget()
        self.HB.addWidget(self.Camera_Version)
        self.HB.addWidget(self.Warning_Widget)
        self.HB.addWidget(self.CAN_Presetting)
        self.VB.addLayout(self.HB)
        self.VB.addWidget(self.CAN_FigurePlot)
        self.setLayout(self.VB)

    def Signal_Def(self):
        '''CAN button connection'''
        self.CAN_Presetting.Signal_load_BDC.connect(self.Load_DBC_Path)
        self.CAN_Presetting.Signal_Ini_CAN.connect(self.Ini_CAN)
        '''CAN button disconnection'''
        self.CAN_Presetting.Signal_Close_CAN.connect(self.Close_CAN)
        '''Visualization option'''
        self.CAN_Presetting.Signal_Ped_Show.connect(self.Ped_Show_Start)
        self.CAN_Presetting.Signal_Veh_Show.connect(self.Veh_Show_Start)
        self.CAN_Presetting.Signal_Lane_Show.connect(self.Lane_Show_Start)
        self.CAN_Presetting.Signal_Clear_Show.connect(self.Clear_Show)
        '''Data Recording'''
        self.CAN_Presetting.Signal_Record_Data.connect(self.Record_Data_Path)
        self.CAN_Presetting.Signal_Save_Data.connect(self.Save_Data)
        '''Video Related, but to be deleted'''
        self.CAN_Presetting.Signal_Open_Vedio.connect(self.Open_Vedio)
        self.CAN_Presetting.Signal_Close_Vedio.connect(self.Close_Vedio)
        '''record video'''
        # self.CAN_Presetting.Signal_Record_Video.connect(self.Record_Vedio)
        self.CAN_Presetting.Signal_Save_Video.connect(self.Save_Vedio)
        '''CAN Data Recording, what is the difference to former one'''
        self.CAN_Channel.Signal_Save.connect(self.Save_CAN_Setting)
        self.CAN_Channel.Signal_Cancel.connect(self.Reset_CAN_Setting)

    def set_default_values(self):
        self.DBC_Path = "./Protocol/Mobileye.dbc"
        self.CAN_Presetting.Line_Load_DBC.setText(self.DBC_Path)
        self.CAN_Channel.Channel_Line.setText('0')
        self.CAN_Channel.Timer0_Line.setText('0x00')
        self.CAN_Channel.Timer1_Line.setText('0x1c')
        self.DBC = kvadblib.Dbc(filename= self.DBC_Path)
        self.nCANInd = int(self.CAN_Channel.Channel_Line.text())
        self.TIMER0 = int(self.CAN_Channel.Timer0_Line.text(), 16)
        self.TIMER1 = int(self.CAN_Channel.Timer1_Line.text(), 16)
        self.CAN_Device = CAN_Device_Set(nDeviceType=4, nDeviceInd=0, nReserved=0, nCANInd=self.nCANInd)
        self.CAN_Presetting.Line_Ini_CAN.setText('AUTO INITIALIZED')
        self.CAN_Presetting.Line_Close_CAN.setText('CAN IS OPEN ')
        self.OpenCAN = 'Yes'
        self.CAN_FigurePlot.Original()
        self.Thread_Msg_Ped_Rec_Indicator = 'Start'
        threading.Thread(target=self.CAN_Msg_Receive).start()
        self.Ped_Show_Start()
        self.Veh_Show_Start()
        self.Lane_Show_Start()

    def Load_DBC_Path(self):
        self.CAN_Presetting.Line_Load_DBC.clear()
        openfile_name = QFileDialog.getOpenFileName(self, 'SELECT DBC FILE','./')
        if openfile_name[0].split('.')[-1:][0] == 'dbc':
            self.DBC_Path = openfile_name[0]
            self.CAN_Presetting.Line_Load_DBC.setText(self.DBC_Path)
        else:
            QMessageBox.warning(self, 'MESSAGE', 'PLEASE LOAD CORRECT DBC FILE!',QMessageBox.Yes)

    '''点击Initial后弹出参数设置的窗口'''
    def Ini_CAN(self):
        '''如果DBC未加载，提示首先加载DBC文件'''
        if self.CAN_Presetting.Line_Load_DBC.text() == '':
            QMessageBox.warning(self, 'MESSAGE', 'PLEASE LOAD DBC FIRST!', QMessageBox.Yes)
        else:
            self.CAN_Channel.show()
            self.CAN_Channel.exec_()

    '''这个意义不大'''
    def Reset_CAN_Setting(self):
        self.CAN_Channel.Channel_Line.setText('0')
        self.CAN_Channel.Timer0_Line.setText('0x00')
        self.CAN_Channel.Timer1_Line.setText('0x1c')

    def Save_CAN_Setting(self):
        self.DBC = kvadblib.Dbc(filename= self.DBC_Path)
        '''设置CAN的通道和波特率'''
        self.nCANInd = int(self.CAN_Channel.Channel_Line.text())
        self.TIMER0 = int(self.CAN_Channel.Timer0_Line.text(), 16)
        self.TIMER1 = int(self.CAN_Channel.Timer1_Line.text(), 16)
        '''定义CAN设备结构体vic'''
        self.vic = CAN_Par_Set(Acc_Code=0x00000000, Acc_Mask=0xffffffff, Filt=0, BPS1=self.TIMER0, BPS2=self.TIMER1, Mod=0)
        '''定义行人报文的结构体vco'''
        self.vco_Ped = VCI_CAN_OBJ()

        '''初始化设备结构函数'''
        self.CAN_Device = CAN_Device_Set(nDeviceType=4, nDeviceInd=0, nReserved=0, nCANInd=self.nCANInd)

        '''判断CAN设备是否初始完成并打开，如果打开，将标志位OpenCAN 设置为Yes'''
        if self.Thread_Msg_Ped_Rec_Indicator == 'Stop':
            self.CAN_Presetting.Line_Ini_CAN.setText(self.CAN.CAN_INITIAL_Result()[1])
            self.CAN_Presetting.Line_Close_CAN.setText('CAN IS OPEN ')
            self.OpenCAN = 'Yes'
            '''画出摄像头原点'''
            self.CAN_FigurePlot.Original()
            '''接收行人报文的线程开启,如果CAN设备初始化完成并打开，把线程标志位Thread_Msg_Ped_Rec_Indicator设为'Start'，
            同时开启行人报文接收的线程'''
            self.Thread_Msg_Ped_Rec_Indicator = 'Start'
            '''开启CAN报文接收的线程'''
            threading.Thread(target=self.CAN_Msg_Receive).start()
        
    '''接收行人报文的函数'''
    def CAN_Msg_Receive(self):
        parser = argparse.ArgumentParser(
        description="Listen on a CAN channel and print all signals received, as specified by a database.")
        parser.add_argument('channel', type=int, default=0, nargs='?', help=(
            "The channel to listen on."))
        parser.add_argument('--db', default="./Protocol/Mobileye.dbc", help=(
            "The database file to look up messages and signals in."))
        parser.add_argument('--bitrate', '-b', default='500k', help=(
            "Bitrate, one of " + ', '.join(bitrates.keys())))
        parser.add_argument('--ticktime', '-t', type=float, default=0, help=(
            "If greater than zero, display 'tick' every this many seconds"))
        args = parser.parse_args()

        #self.monitor_channel(args.channel, args.db, bitrates[args.bitrate.upper()], args.ticktime)
        channel_number = args.channel
        db_name = args.db
        bitrate = bitrates[args.bitrate.upper()]
        ticktime = args.ticktime
        
        db = kvadblib.Dbc(filename=db_name)

        ch = canlib.openChannel(channel_number, canlib.canOPEN_ACCEPT_VIRTUAL)
        ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
        ch.setBusParams(bitrate)
        ch.busOn()

        timeout = 0.5
        tick_countup = 0
        if ticktime <= 0:
            ticktime = None
        elif ticktime < timeout:
            timeout = ticktime

        while True:
            '''判断线程是否需要关闭'''
            if self.Thread_Msg_Ped_Rec_Indicator == 'Stop':
                break
            else:
                try:
                    frame = ch.read(timeout=int(timeout * 1000))
                    self.Result = frame
                    self.CAN_Msg_Analysis_Result()
                    if self.Record_Data_Indicator == 'Yes':
                        self.writer.writerow([hex(self.Result[0]), self.Result[2], self.Result[1].hex(),self.Result[3]])

                except canlib.CanNoMsg:
                    print("fail")
                    if ticktime is not None:
                        tick_countup += timeout 
                        while tick_countup > ticktime:
                            print("tick")
                            tick_countup -= ticktime
                

    '''DBC解析行人CAN报文'''
    def CAN_Msg_Analysis_Result(self):
        '''首先处理障碍物的报文'''
        
        if self.Result[0] in self.CAN_FigurePlot.Obstacle.CAN_Obstacle_ID[:, 0]:
            '''所有障碍物报文都在这里解析'''
            self.Signal_Obstacle = CAN_Msg_Analysis().analysis(self.Result[0], bytearray(self.Result[1]), self.DBC)
            '''因为障碍物报文不区分车和行人，但是障碍x物的ID是固定的，一个ID只能对应一个人或者障碍物'''
            self.Index = int(float(self.Signal_Obstacle['Obstacle_ID']))
            '''首先处理人的报文'''
            if self.Signal_Obstacle['Obstacle_Type'] == 'Ped' or self.Signal_Obstacle['Obstacle_Type'] == 'Bike' \
                    or self.Signal_Obstacle['Obstacle_Type'] == 'Bicycle':
                '''因为Mobileye识别到人才会输出相关报文，所以需要监测该报文对应的人（有一个唯一的ID号）在
                下一时刻是否还会继续出现，如果不出现了，说明人没有识别到了，需要清除这个人的位置信息，不在
                图上画出来。这里采用的方法是，对于行人，有一个64x2的矩阵，开始的时候矩阵全部为0，当接收到
                一个行人的报文的时候，在其对应的ID的矩阵位置（比如：ID = 32，则对应矩阵的第32行），将矩阵
                （32，0）元素的值赋给（32，1），然后（32，0）的元素值+1。然后将该行人的坐标位置放置在行人
                坐标向量中。'''
                self.Data_Ped_Counter[self.Index, 1] = self.Data_Ped_Counter[self.Index, 0]
                self.Data_Ped_Counter[self.Index, 0] += 1
                self.CAN_FigurePlot.Obstacle.Ped_X[self.Index] = float(self.Signal_Obstacle['Obstacle_Position_X'])
                self.CAN_FigurePlot.Obstacle.Ped_Y[self.Index] = float(self.Signal_Obstacle['Obstacle_Position_Y'])

                '''对于车辆也是一样的处理方法'''
            elif self.Signal_Obstacle['Obstacle_Type'] == 'Vehicle' or self.Signal_Obstacle['Obstacle_Type'] == 'Truck':
                self.Data_Veh_Counter[self.Index, 1] = self.Data_Veh_Counter[self.Index, 0]
                self.Data_Veh_Counter[self.Index, 0] += 1
                self.CAN_FigurePlot.Obstacle.Veh_X[self.Index] = float(self.Signal_Obstacle['Obstacle_Position_X'])
                self.CAN_FigurePlot.Obstacle.Veh_Y[self.Index] = float(self.Signal_Obstacle['Obstacle_Position_Y'])
            else:
                pass

            '''这里对行人或者车辆是否消失进行判断：0x738是一个反映障碍物检测结果的报文，与是否有障碍物无关，
            每个CAN报文发送周期都有（或者找一个其他的报文，只要这个报文在每次CAN报文接收循环里面都出现即可），
            每当检测到这个报文的时候，就去看行人和车辆的计数器矩阵：首先给计数器矩阵的第二列元素都+1，然后用
            第二列元素减去第一列元素，找到结果为1的元素所在的‘行’，则说明这些‘行’对应的障碍物信息在上一个
            周期内没有接收到，障碍物丢失了，所以这些障碍物的位置信息因该清除。'''
        elif self.Result[0] in self.CAN_FigurePlot.Obstacle.CAN_Obstacle_TotalInf_ID:
            '''判断行人'''
            self.Obstacle_State = CAN_Msg_Analysis().analysis(self.Result[0], bytearray(self.Result[1]), self.DBC)
            self.Warning_Widget.updateCamState(self.Obstacle_State['Failsafe'])
            self.Warning_Widget.updateNumOfObs(self.Obstacle_State['Number_of_Obstacles'])
            self.Data_Ped_Counter[:, 1] += 1
            self.Data_Tem_Ped_Index = self.Data_Ped_Counter[:, 1] - self.Data_Ped_Counter[:, 0]
            self.Data_Delet_Ped_Index = np.argwhere(self.Data_Tem_Ped_Index == 1)
            self.Data_Ped_Counter[self.Data_Delet_Ped_Index] = 0
            self.CAN_FigurePlot.Obstacle.Ped_X[self.Data_Delet_Ped_Index] = 0
            self.CAN_FigurePlot.Obstacle.Ped_Y[self.Data_Delet_Ped_Index] = 0
            '''判断车辆'''
            self.Data_Veh_Counter[:, 1] += 1
            self.Data_Tem_Veh_Index = self.Data_Veh_Counter[:, 1] - self.Data_Veh_Counter[:, 0]
            self.Data_Delet_Veh_Index = np.argwhere(self.Data_Tem_Veh_Index == 1)
            self.Data_Veh_Counter[self.Data_Delet_Veh_Index] = 0
            self.CAN_FigurePlot.Obstacle.Veh_X[self.Data_Delet_Veh_Index] = 0
            self.CAN_FigurePlot.Obstacle.Veh_Y[self.Data_Delet_Veh_Index] = 0

            '''处理车道线，每条车道线一共有4个参数表示，分别放在2条报文中，一条报文3个C0C2C3，一条报文1个C1。左侧车道线
            的参数在数据向量中的索引值为0，右侧的索引值为1'''
        elif self.Result[0] in self.CAN_FigurePlot.Lane.CAN_LANE_ID :
            self.Signal_Lane = CAN_Msg_Analysis().analysis(self.Result[0], bytearray(self.Result[1]), self.DBC)
            if self.Result[0] == self.CAN_FigurePlot.Lane.CAN_Ego_Left_Lane_ID[0] or \
                    self.Result[0] == self.CAN_FigurePlot.Lane.CAN_Ego_Right_Lane_ID[0]:
                Index_Lane_C023 = int((self.Result[0] - 0x766) / 2)
                self.CAN_FigurePlot.Lane.Lane_C0[Index_Lane_C023] = float(self.Signal_Lane['Curve_Parameter_C0'])
                self.CAN_FigurePlot.Lane.Lane_C2[Index_Lane_C023] = float(self.Signal_Lane['Curve_Parameter_C2'])
                self.CAN_FigurePlot.Lane.Lane_C3[Index_Lane_C023] = float(self.Signal_Lane['Curve_Parameter_C3'])

            elif self.Result[0] == self.CAN_FigurePlot.Lane.CAN_Ego_Left_Lane_ID[1] or self.Result[0] == \
                    self.CAN_FigurePlot.Lane.CAN_Ego_Right_Lane_ID[1]:
                Index_Lane_C1 = int((self.Result[0] - 0x767)/2)
                self.CAN_FigurePlot.Lane.Lane_C1[Index_Lane_C1] = float(self.Signal_Lane['Curve_Parameter_C1'])
            
            elif self.Result[0] in self.CAN_FigurePlot.Lane.CAN_Next_Left_Lane_ID.reshape([4,2])[:,0] or \
                self.Result[0] in self.CAN_FigurePlot.Lane.CAN_Next_Right_Lane_ID.reshape([4,2])[:,0]:
                Index_Next_Lane = int((self.Result[0] - 0x76C) / 4)
                Index_Lane_C023 = int((self.Result[0] - 0x76C) % 4 // 2)
                self.CAN_FigurePlot.Lane.Next_Lane_C0[Index_Next_Lane][Index_Lane_C023] = float(self.Signal_Lane['Curve_Parameter_C0'])
                self.CAN_FigurePlot.Lane.Next_Lane_C2[Index_Next_Lane][Index_Lane_C023] = float(self.Signal_Lane['Curve_Parameter_C2'])
                self.CAN_FigurePlot.Lane.Next_Lane_C3[Index_Next_Lane][Index_Lane_C023] = float(self.Signal_Lane['Curve_Parameter_C3'])
            
            elif self.Result[0] in self.CAN_FigurePlot.Lane.CAN_Next_Left_Lane_ID.reshape([4,2])[:,1] or \
                self.Result[0] in self.CAN_FigurePlot.Lane.CAN_Next_Right_Lane_ID.reshape([4,2])[:,1]:
                Index_Next_Lane = int((self.Result[0] - 0x76D) / 4)
                Index_Lane_C1 = int((self.Result[0] - 0x76D) % 4 // 2)
                self.CAN_FigurePlot.Lane.Next_Lane_C1[Index_Next_Lane][Index_Lane_C1] = float(self.Signal_Lane['Curve_Parameter_C1'])
            
            else:
                pass
            [Lane_X, Lane_Y] = \
                Coordinate().Lane_XY_Calculate(self.CAN_FigurePlot.Lane.Lane_C0, self.CAN_FigurePlot.Lane.Lane_C1, \
                                               self.CAN_FigurePlot.Lane.Lane_C2, self.CAN_FigurePlot.Lane.Lane_C3)

            [Next_Lane_X, Next_Lane_Y] = \
                Coordinate().Next_Lane_XY_Calculate(self.CAN_FigurePlot.Lane.Next_Lane_C0, self.CAN_FigurePlot.Lane.Next_Lane_C1, \
                                               self.CAN_FigurePlot.Lane.Next_Lane_C2, self.CAN_FigurePlot.Lane.Next_Lane_C3)

            self.CAN_FigurePlot.Lane.Lane_X = np.concatenate((Lane_X, Next_Lane_X),axis=0)
            self.CAN_FigurePlot.Lane.Lane_Y = np.concatenate((Lane_Y, Next_Lane_Y),axis=0)
        elif self.Result[0] in self.CAN_FigurePlot.Vehicle.Vehicle_State:
            if self.Result[0] == self.CAN_FigurePlot.Vehicle.Vehicle_State[0]:
                self.Vehicle_State = CAN_Msg_Analysis().analysis(self.Result[0], bytearray(self.Result[1]), self.DBC)
                self.Warning_Widget.updateEgoSpeed(self.Vehicle_State['Speed'])
                
        else:
            pass

    '''绘制行人的图像'''
    def Ped_Show_Start(self):
        '''仅当CAN设备开启的情况下才允许绘图'''
        if self.OpenCAN == 'Yes':
            self.CAN_FigurePlot.Timer_Cur_Ped.start(1)
        else:
            QMessageBox.information(self, 'INFORMATION', 'PLEASE OPEN CAN DEVICE', QMessageBox.Yes)

    '''绘制车辆的图像'''
    def Veh_Show_Start(self):
        if self.OpenCAN == 'Yes':
            self.CAN_FigurePlot.Timer_Cur_Veh.start(1)
        else:
            QMessageBox.information(self, 'Information', 'PLEASE OPEN CAN DEVICE', QMessageBox.Yes)

    '''绘制车道线的图像'''
    def Lane_Show_Start(self):
        if self.OpenCAN == 'Yes':
            self.CAN_FigurePlot.Timer_Cur_Lane.start(1)
        else:
            QMessageBox.information(self, 'Information', 'PLEASE OPEN CAN DEVICE', QMessageBox.Yes)

    '''清除所有的图像，停止QTimer绘图并清除图像'''
    def Clear_Show(self):
        self.CAN_FigurePlot.Timer_Stop()

    ###############'''CAN报文数据模块'''####################
    '''开始记录数据，当前只支持csv文件'''
    def Record_Data_Path(self):
        if self.OpenCAN == 'Yes' and self.Record_Data_Indicator == 'No':
            # self.Save_File_Name = QFileDialog.getSaveFileName(self, 'PLEASE SELECT THE SAVE PATH', './')[0]
            # if self.Save_File_Name.split() == []:
            #     QMessageBox.information(self, 'Information', 'PLEASE CHOOSE PATH AND FILE', QMessageBox.Yes)
            # else:
            QMessageBox.information(self, 'Information', 'Start Recording', QMessageBox.Yes)
            self.Record_Data(' ', self.Record_Data_Counter)
            self.Record_Data_Indicator = 'Yes'
        else:
            QMessageBox.information(self, 'Information', 'CAN NOT OPEN or DATA IS RECORDING', QMessageBox.Yes)

    def Record_Data(self, Save_Data_Path, Counter):
        self.csvfile = open('Mobileye'+ '_' + time.strftime('%m%d') + '_' + time.strftime('%H%M%S') + '.csv', 'w', newline='')
        self.writer = csv.writer(self.csvfile)
        self.writer.writerow(['Identifier', 'DLC', 'Data', 'Time'])

    '''保存数据'''
    def Save_Data(self):
        if self.Record_Data_Indicator == 'Yes':
            res = QMessageBox.warning(self, 'MESSAGE', 'STOP RECORD and SAVE DATA?', \
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if res == QMessageBox.Yes:
                self.Record_Data_Indicator = 'No'
                self.csvfile.close()
                self.Record_Data_Counter = 0
            else:
                pass
        else:
            QMessageBox.information(self, 'Information', 'NO CAN DATA RECORD', QMessageBox.Yes)

    ##################'''视频模块'''###########################
    '''开启视频'''
    def Open_Vedio(self):
        res = QMessageBox.warning(self, 'MESSAGE', 'Yes = MobileNet , No = YOLO4 Tiny', \
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if self.Camera_Version.Vedio_Running_Indicator == 'Yes':
            QMessageBox.information(self, 'Information', 'VIDEO IS OPEN', QMessageBox.Yes)
        else:
            self.Camera_Version.Vedio_Running_Indicator = 'Yes'
            if res == QMessageBox.Yes:
                self.Camera_Version.Open_Vedio_Initial('MobileNet')
            else : 
                self.Camera_Version.Open_Vedio_Initial('YOLO4')
            self.Camera_Version.Timer_Start()
            

    '''关闭视频'''
    def Close_Vedio(self):
        if self.Camera_Version.Vedio_Running_Indicator == 'No':
            QMessageBox.information(self, 'Information', 'VEDIO IS CLOSED', QMessageBox.Yes)
        elif self.Camera_Version.Vedio_Recording_Indicator == 'Yes':
            QMessageBox.information(self, 'Information', 'VEDIO IS RECORDING, PLEASE SAVE', QMessageBox.Yes)
        else:
            self.Camera_Version.Vedio_Running_Indicator = 'No'
            self.Camera_Version.Vedio_Recording_Indicator = 'No' 
            self.Camera_Version.Vedio_Winndow.setPixmap(QPixmap('./Pic/No_Video.jpg'))
            
            
    def Close_Vedio_Without_Message(self):
        self.Camera_Version.Vedio_Running_Indicator = 'No'
        self.Camera_Version.Vedio_Recording_Indicator = 'No'

    '''录制视频,当前只支持avi文件'''
    def Record_Vedio(self):
        if self.Camera_Version.Vedio_Running_Indicator == 'Yes' and self.Camera_Version.Vedio_Recording_Indicator == 'No':
            Vedio_Save_Path = QFileDialog.getSaveFileName(self, 'PLEASE SELECT THE SAVE PATH', './')[0]
            if Vedio_Save_Path.split() == []:
                QMessageBox.information(self, 'Information', 'PLEASE CHOOSE PATH AND FILE', QMessageBox.Yes)
            else:
                self.Camera_Version.Vedio_Save_Path = Vedio_Save_Path
                self.Camera_Version.Record_Vedio_Initial(self.Camera_Version.Vedio_Save_Path)
                self.Camera_Version.Vedio_Recording_Indicator = 'Yes'
        else:
            QMessageBox.information(self, 'Information', 'VEDIO IS CLOSED OR RECORDING', QMessageBox.Yes)

    '''保存视频'''
    def Save_Vedio(self):
        if self.Camera_Version.Vedio_Recording_Indicator == 'Yes':
            res = QMessageBox.warning(self, 'MESSAGE', 'CLOSE VEDIO AND SAVE?', \
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if res == QMessageBox.Yes:
                self.Camera_Version.Vedio_Recording_Indicator = 'Save'
            else:
                pass
        else:
            QMessageBox.information(self, 'Information', 'NO VIDEO RECORD', QMessageBox.Yes)

    '''关闭软件功能'''
    def Close_CAN(self):
        if self.CAN_Presetting.Line_Close_CAN.text() == 'CAN DEVICE NOT OPEN':
            QMessageBox.warning(self, 'MESSAGE', 'CAN DEVICE NOT OPEN!', QMessageBox.Yes)
        else:

            #res = QMessageBox.warning(self, 'MESSAGE','CLOSE CAN DEVICE?', \
            #                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            #if res == QMessageBox.Yes:
            if True:
                '''停止所有线程'''
                self.Stop_Thread()
                '''停止绘图'''
                self.CAN_FigurePlot.Timer_Stop()
                self.CAN_FigurePlot.Clear_Original()
                '''清除已经画的所有图像'''
                self.Windows_Clear()
                '''所有的状态标志位复位'''
                self.Return_Initial_State()
            else:
                pass

    '''这个是总开关'CLOSE'关闭所有线程的函数'''
    def Stop_Thread(self):
        self.Thread_Msg_Ped_Rec_Indicator = 'Stop'

    '''清除界面上显示的文字信息'''
    def Windows_Clear(self):
        self.CAN_Presetting.Line_Ini_CAN.clear()
        self.CAN_Presetting.Line_Load_DBC.clear()
        self.CAN_Presetting.Line_Close_CAN.clear()


    '''状态标志复位'''
    def Return_Initial_State(self):
        self.OpenCAN = 'No'
        self.Record_Data_Indicator = 'No'
        self.Record_Data_Counter = 0
        self.Data_Ped_Counter = np.zeros([64, 2])
        self.Data_Veh_Counter = np.zeros([64, 2])

    def closeEvent(self,event):
        self.Close_Vedio_Without_Message()
        self.Close_CAN()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    Mainwindow = MainWindows()
    Mainwindow.show()
    sys.exit(app.exec_())
