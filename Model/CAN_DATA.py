import numpy as np

class CAN_Data_Obstacle:
    '''障碍物坐标向量'''
    Ped_X = np.zeros(64)
    Ped_Y = np.zeros(64)
    Veh_X = np.zeros(64)
    Veh_Y = np.zeros(64)
    Veh_Relative_Vel_X = np.ones(64)*(1000)
    Veh_Cut_State = ['Undefined']*64
    '''障碍物报文ID'''
    CAN_Obstacle_TotalInf_ID = np.array([0x738])
    CAN_Obstacle_A_ID = np.array([0x739, 0x73c, 0x73f, 0x742, 0x745, 0x748, 0x74b, 0x74e, 0x751, 0x754, 0x757, 0x75a, 0x75d])
    CAN_Obstacle_B_ID = np.array([0x73a, 0x73d, 0x740, 0x743, 0x746, 0x749, 0x74c, 0x74f, 0x752, 0x755, 0x758, 0x75b, 0x75e])
    CAN_Obstacle_C_ID = np.array([0x73b, 0x73e, 0x741, 0x744, 0x747, 0x74a, 0x74d, 0x750, 0x753, 0x756, 0x759, 0x75c, 0x75f])
    CAN_Obstacle_ID = np.transpose(np.array([CAN_Obstacle_A_ID, CAN_Obstacle_B_ID, CAN_Obstacle_C_ID]))
    def __init__(self):
        pass

class CAN_Data_Lane:
    '''车道线参数向量'''
    Lane_C0 = np.zeros(2).reshape(2,1)
    Lane_C1 = np.zeros(2).reshape(2,1)
    Lane_C2 = np.zeros(2).reshape(2,1)
    Lane_C3 = np.zeros(2).reshape(2,1)
    Lane_X = np.zeros([10, 50])
    Lane_Y = np.zeros([10, 50])

    Next_Lane_C0 = np.zeros(8).reshape(4,2,1)
    Next_Lane_C1 = np.zeros(8).reshape(4,2,1)
    Next_Lane_C2 = np.zeros(8).reshape(4,2,1)
    Next_Lane_C3 = np.zeros(8).reshape(4,2,1)
    Next_Lane_X = np.zeros([4, 2, 50])
    Next_Lane_Y = np.zeros([4, 2, 50])


    '''车道线报文ID'''
    CAN_Ego_Left_Lane_ID = [0x766, 0x767]
    CAN_Ego_Right_Lane_ID = [0x768, 0x769]

    CAN_Ego_Lane_Reference_Point_ID = [0x76a]
    CAN_Number_Of_Next_Lane_ID = [0x76b]
    '''旁白车道线的ID，不用'''

    CAN_Next_Left_Lane0_ID = [0x76c, 0x76d]
    CAN_Next_Left_Lane1_ID = [0x770, 0x771]
    CAN_Next_Left_Lane2_ID = [0x774, 0x775]
    CAN_Next_Left_Lane3_ID = [0x778, 0x779]
    CAN_Next_Left_Lane_ID = np.concatenate((CAN_Next_Left_Lane0_ID,CAN_Next_Left_Lane1_ID,CAN_Next_Left_Lane2_ID,CAN_Next_Left_Lane3_ID), axis=None)

    CAN_Next_Right_Lane0_ID = [0x76e, 0x76f]
    CAN_Next_Right_Lane1_ID = [0x772, 0x773]
    CAN_Next_Right_Lane2_ID = [0x776, 0x777]
    CAN_Next_Right_Lane3_ID = [0x77a, 0x77b]
    CAN_Next_Right_Lane_ID = np.concatenate((CAN_Next_Right_Lane0_ID,CAN_Next_Right_Lane1_ID,CAN_Next_Right_Lane2_ID,CAN_Next_Right_Lane3_ID), axis=None)

    CAN_LANE_ID = np.concatenate((CAN_Ego_Left_Lane_ID, CAN_Ego_Right_Lane_ID,CAN_Next_Left_Lane_ID,CAN_Next_Right_Lane_ID), axis=None)

    def __init__(self):
        pass

    def reset(self):
        self.Lane_C0 = np.zeros(2).reshape(2,1)
        self.Lane_C1 = np.zeros(2).reshape(2,1)
        self.Lane_C2 = np.zeros(2).reshape(2,1)
        self.Lane_C3 = np.zeros(2).reshape(2,1)
        self.Lane_X = np.zeros([10, 50])
        self.Lane_Y = np.zeros([10, 50])
        
        self.Next_Lane_C0 = np.zeros(8).reshape(4,2,1)
        self.Next_Lane_C1 = np.zeros(8).reshape(4,2,1)
        self.Next_Lane_C2 = np.zeros(8).reshape(4,2,1)
        self.Next_Lane_C3 = np.zeros(8).reshape(4,2,1)
        self.Next_Lane_X = np.zeros([4, 2, 50])
        self.Next_Lane_Y = np.zeros([4, 2, 50])

class CAN_Data_Vehicle:
    #Vehicle_State = [0x700, 0x760, 0x738]
    Vehicle_State = [0x760, 0x738]
    def __init__(self):
        pass