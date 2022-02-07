import sys
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import depthai as dai
import threading
import qdarkstyle
import numpy as np

class Camera_Version(QWidget):
    Vedio_Running_Indicator = 'No'
    Vedio_Recording_Indicator = 'No'
    Vedio_Save_Path = ''
    '''每Vedio_Number帧保存一个视频'''
    Record_Vedio_Counter = int(0)
    Vedio_Number = 90000#一个小时保存一个视频
    def __init__(self, parent = None):
        super(Camera_Version, self).__init__(parent)
        self.SetUI()

    def SetUI(self):
        self.resize(540,360)
        self.setWindowTitle('Camera Version')
        self.FixedHeight = 30
        self.Font = QFont()
        self.Font.setPixelSize(18)

        self.Vedio_Winndow = QLabel()
        self.Vedio_Winndow.setFixedSize(444,250)
        self.Vedio_Winndow.setScaledContents (True)#让图片自适应大小
        self.init_image = QPixmap('./Pic/No_Video.jpg')
        self.Vedio_Winndow.setPixmap(self.init_image)

        layout = QVBoxLayout()
        layout.addWidget(self.Vedio_Winndow)
        self.setLayout(layout)

    def Open_Vedio_Initial(self,option):
        if option == 'MobileNet':
            self.settingMobileNet()

        elif option == 'YOLO4':
            self.settingYOLO4()

        else:
            QMessageBox.information(self, 'Information', 'Error', QMessageBox.Yes)
            self.Camera_Version.Vedio_Running_Indicator = 'No'

    def Timer_Start(self):
        threading.Thread(target=self.Vedio_Show).start()

    def Record_Vedio_Initial(self,Vedio_Save_Path):
        fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')#('M', 'P', '4', '2')
        '''主程序调用这个函数的时候，会把路径信息传递进来，这样就可以在这个界面里面读取到路径信息了'''
        if self.Record_Vedio_Counter == 0:
            self.Path = Vedio_Save_Path
        else:
            pass
        self.out = cv2.VideoWriter(Vedio_Save_Path + '.avi', fourcc, 25.0, (1280, 720))

    def Vedio_Show(self):
        
        with dai.Device(self.pipeline) as device:
            self.qVideo = device.getOutputQueue(name="video", maxSize=4, blocking=False)
            self.qPreview = device.getOutputQueue(name="preview", maxSize=4, blocking=False)
            self.qDet = device.getOutputQueue(name="nn", maxSize=4, blocking=False)
            
            self.videoFrame = None
            self.detections = []
            
            def frameNorm(frame, bbox):
                normVals = np.full(len(bbox), frame.shape[0])
                normVals[::2] = frame.shape[1]
                return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

            def displayFrame(frame):
                color = (255, 0, 0)
                for detection in self.detections:
                    bbox = frameNorm(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
                    cv2.putText(frame, self.labelMap[detection.label], (bbox[0] + 10, bbox[1] + 200), cv2.FONT_HERSHEY_SIMPLEX, 5, color,thickness=3)
                    cv2.putText(frame, f"{int(detection.confidence * 100)}%", (bbox[0] + 10, bbox[1] + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, color)
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                return frame 
            
            while self.Vedio_Running_Indicator == 'Yes':
                self.inVideo = self.qVideo.tryGet()
                self.inPreview = self.qPreview.tryGet()
                self.inDet = self.qDet.tryGet()
                if self.inVideo is not None:
                    self.videoFrame = self.inVideo.getCvFrame()
                    
                if self.inDet is not None:
                    self.detections = self.inDet.detections
                    
                if self.inPreview is not None:
                    pass 
                
                if self.videoFrame is not None:
                    frame = displayFrame(self.videoFrame)
                    frame_ = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    img = QImage(frame_.data, frame_.shape[1], frame_.shape[0], QImage.Format_RGB888)
                    self.Vedio_Winndow.setPixmap(QPixmap.fromImage(img))
                    
            if self.Vedio_Running_Indicator == 'No':
                self.Vedio_Winndow.setPixmap(self.init_image)
                
    def Save_Vedio(self):
        self.out.release()
        self.Record_Vedio_Counter = int(0)
        self.Vedio_Recording_Indicator = 'No'

    def Close_Vedio(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.Vedio_Winndow.setPixmap(self.init_image)
        self.Record_Vedio_Counter = int(0)
        
    def settingMobileNet(self):
        self.nnPath = str((Path(__file__).parent / Path('../models/mobilenet-ssd_openvino_2021.4_6shave.blob')).resolve().absolute())
        self.labelMap = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
            "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
        self.pipeline = dai.Pipeline()
        self.camRgb = self.pipeline.create(dai.node.ColorCamera)
        self.nn = self.pipeline.create(dai.node.MobileNetDetectionNetwork)

        self.xoutVideo = self.pipeline.create(dai.node.XLinkOut)
        self.xoutPreview = self.pipeline.create(dai.node.XLinkOut)
        self.nnOut = self.pipeline.create(dai.node.XLinkOut)

        self.xoutVideo.setStreamName("video")
        self.xoutPreview.setStreamName("preview")
        self.nnOut.setStreamName("nn")

        # Properties
        
        self.camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        self.camRgb.setInterleaved(False)
        self.camRgb.setPreviewKeepAspectRatio(False)
        # Define a neural network that will make predictions based on the source frames
        self.nn.setConfidenceThreshold(0.5)
        self.nn.setBlobPath(self.nnPath)
        self.nn.setNumInferenceThreads(2)
        self.nn.input.setBlocking(False)

        # Linking
        self.camRgb.video.link(self.xoutVideo.input)
        self.camRgb.preview.link(self.xoutPreview.input)
        self.camRgb.preview.link(self.nn.input)
        self.nn.out.link(self.nnOut.input)
        
    def settingYOLO4(self):
        self.nnPath = str((Path(__file__).parent / Path('../models/yolo-v4-tiny-tf_openvino_2021.4_6shave.blob')).resolve().absolute())
        self.labelMap = [
    "person",         "bicycle",    "car",           "motorbike",     "aeroplane",   "bus",           "train",
    "truck",          "boat",       "traffic light", "fire hydrant",  "stop sign",   "parking meter", "bench",
    "bird",           "cat",        "dog",           "horse",         "sheep",       "cow",           "elephant",
    "bear",           "zebra",      "giraffe",       "backpack",      "umbrella",    "handbag",       "tie",
    "suitcase",       "frisbee",    "skis",          "snowboard",     "sports ball", "kite",          "baseball bat",
    "baseball glove", "skateboard", "surfboard",     "tennis racket", "bottle",      "wine glass",    "cup",
    "fork",           "knife",      "spoon",         "bowl",          "banana",      "apple",         "sandwich",
    "orange",         "broccoli",   "carrot",        "hot dog",       "pizza",       "donut",         "cake",
    "chair",          "sofa",       "pottedplant",   "bed",           "diningtable", "toilet",        "tvmonitor",
    "laptop",         "mouse",      "remote",        "keyboard",      "cell phone",  "microwave",     "oven",
    "toaster",        "sink",       "refrigerator",  "book",          "clock",       "vase",          "scissors",
    "teddy bear",     "hair drier", "toothbrush"
]
        self.pipeline = dai.Pipeline()
        self.camRgb = self.pipeline.create(dai.node.ColorCamera)
        self.nn = self.pipeline.create(dai.node.YoloDetectionNetwork)

        self.xoutVideo = self.pipeline.create(dai.node.XLinkOut)
        self.xoutPreview = self.pipeline.create(dai.node.XLinkOut)
        self.nnOut = self.pipeline.create(dai.node.XLinkOut)

        self.xoutVideo.setStreamName("video")
        self.xoutPreview.setStreamName("preview")
        self.nnOut.setStreamName("nn")

        # Properties
        self.camRgb.setPreviewSize(416, 416)
        self.camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        self.camRgb.setInterleaved(False)
        self.camRgb.setPreviewKeepAspectRatio(False)
        # Define a neural network that will make predictions based on the source frames
        
        self.nn.setConfidenceThreshold(0.5)
        self.nn.setNumClasses(80)
        self.nn.setCoordinateSize(4)
        self.nn.setAnchors(np.array([10, 14, 23, 27, 37, 58, 81, 82, 135, 169, 344, 319]))
        self.nn.setAnchorMasks({"side26": np.array([1, 2, 3]), "side13": np.array([3, 4, 5])})
        self.nn.setBlobPath(self.nnPath)
        self.nn.setNumInferenceThreads(2)
        self.nn.input.setBlocking(False)

        # Linking
        self.camRgb.video.link(self.xoutVideo.input)
        self.camRgb.preview.link(self.xoutPreview.input)
        self.camRgb.preview.link(self.nn.input)
        self.nn.out.link(self.nnOut.input)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    win = Camera_Version()
    win.show()
    sys.exit(app.exec_())

