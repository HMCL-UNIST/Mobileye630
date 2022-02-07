import numpy as np

'''坐标计算，将距离和角度转化为摄像头坐标系的X-Y坐标'''
class Coordinate:
    def __init__(self):
        pass

    def XY_Calculate(self, Angle, Distance):
        self.X = Distance * np.cos(Angle * (np.pi / 180))
        self.Y = Distance * np.sin(Angle * np.pi / 180)
        return [self.X, self.Y]

    def Lane_XY_Calculate(self,Lane_C0, Lane_C1, Lane_C2, Lane_C3):
        self.X_Lane = np.arange(0,50,1)*np.ones([2,50])
        self.Y_Lane = -(Lane_C0 + Lane_C1*self.X_Lane + Lane_C2*pow(self.X_Lane,2)+ Lane_C3*pow(self.X_Lane,3))
        return [self.X_Lane, self.Y_Lane]

    def Next_Lane_XY_Calculate(self,Lane_C0, Lane_C1, Lane_C2, Lane_C3):
        self.X_Lane = np.arange(0,50,1)*np.ones([4,2,50])
        self.Y_Lane = -(Lane_C0 + Lane_C1*self.X_Lane + Lane_C2*pow(self.X_Lane,2)+ Lane_C3*pow(self.X_Lane,3))
        return [self.X_Lane.reshape(8,50), self.Y_Lane.reshape(8,50)]