from canlib import canlib
from canlib.canlib import ChannelData
import time

def sendEgoSpeed(ch1):
    message = [0x01, 0xAF, 0x40, 0x00,0x00,0x00,0x00,0x00]
    ch1.write_raw(int(0x760), message, dlc=8)

def sendLane(ch1):
    message = [ 0xC2, 0x00, 0xFE, 0xFF, 0x7F, 0xFF, 0x7F, 0x00]
    ch1.write_raw(int(0x766),message,dlc=8)
    message = [ 0xFF, 0x7F, 0x00, 0x80]
    ch1.write_raw(int(0x767),message,dlc=4)

    message = [ 0xC2, 0xE0, 0x01, 0xFF, 0x7F, 0xFF, 0x7F, 0x00]
    ch1.write_raw(int(0x768),message,dlc=8)
    message = [ 0xFF, 0x7F, 0x00, 0x80]
    ch1.write_raw(int(0x769),message,dlc=4)

def sendNextLane(ch1):
    message = [0xC2, 0x35, 0xFD, 0x09, 0x78, 0xFF, 0x7F, 0x07]
    ch1.write_raw(int(0x76c),message,dlc=8)
    message = [0x9B, 0x80, 0x00, 0x80]
    ch1.write_raw(int(0x76d),message,dlc=4)

    message = [0xC2,0x09, 0x06, 0xFF, 0x7F ,0xFF, 0x7F, 0x19]
    ch1.write_raw(int(0x76e),message,dlc=8)
    message = [0x6F, 0x7F, 0x00, 0x80]
    ch1.write_raw(int(0x76f),message,dlc=4)

    message = [0xC2, 0x35, 0xFD, 0x09, 0x78, 0xFF, 0x7F, 0x07]
    ch1.write_raw(int(0x770),message,dlc=8)
    message = [0x9B, 0x80, 0x00, 0x80]
    ch1.write_raw(int(0x771),message,dlc=4)

    message = [0xC2, 0x35, 0xFD, 0x09, 0x78, 0xFF, 0x7F, 0x07]
    ch1.write_raw(int(0x772),message,dlc=8)
    message = [0x9B, 0x80, 0x00, 0x80]
    ch1.write_raw(int(0x773),message,dlc=4)
    
    message = [0xC2, 0x35, 0xFD, 0x09, 0x78, 0xFF, 0x7F, 0x07]
    ch1.write_raw(int(0x774),message,dlc=8)
    message = [0x9B, 0x80, 0x00, 0x80]
    ch1.write_raw(int(0x775),message,dlc=4)

    message = [0xC2, 0x35, 0xFD, 0x09, 0x78, 0xFF, 0x7F, 0x07]
    ch1.write_raw(int(0x776),message,dlc=8)
    message = [0x9B, 0x80, 0x00, 0x80]
    ch1.write_raw(int(0x777),message,dlc=4)

    message = [0xC2, 0x35, 0xFD, 0x09, 0x78, 0xFF, 0x7F, 0x07]
    ch1.write_raw(int(0x778),message,dlc=8)
    message = [0x9B, 0x80, 0x00, 0x80]
    ch1.write_raw(int(0x779),message,dlc=4)

    message = [0xC2, 0x35, 0xFD, 0x09, 0x78, 0xFF, 0x7F, 0x07]
    ch1.write_raw(int(0x77a),message,dlc=8)
    message = [0x9B, 0x80, 0x00, 0x80]
    ch1.write_raw(int(0x77b),message,dlc=4)

    '''message = [ 0xC2, 0xE0, 0x01, 0xFF, 0x7F, 0xFF, 0x7F, 0x00]
    ch1.write_raw(int(0x768),message,dlc=8)
    message = [ 0xFF, 0x7F, 0x00, 0x80]
    ch1.write_raw(int(0x769),message,dlc=4)'''

def sendNumOfObs(ch1):
    message = [0x10, 0xB8, 0x00, 0x02, 0x03, 0x00]
    ch1.write_raw(int(0x738),message,dlc=6)    
    
def sendDataFromCsv(ch1,file_name):
    f = open(file_name,"r")
    f.readline()
    for msg in f.readlines():
        print(msg)
        msg = msg.split(",")
        message =[int('0x'+msg[2][i:i+2],16) for i in range(0,len(msg[2]),2)]
        ch1.write_raw(int(msg[0],16),message,dlc=int(msg[1]))
        time.sleep(1/10000000.0)
    
channel = 0
chd = canlib.ChannelData(channel)

file_name = './Mobileye_0126_150803.csv'
print("CANlib version: v{}".format(chd.dll_product_version))
print("canlib dll version: v{}".format(chd.dll_file_version))
print("Using channel: {ch}, EAN: {ean}".format(ch=chd.device_name, ean=chd.card_upc_no))

ch1 = canlib.openChannel(channel, canlib.canOPEN_ACCEPT_VIRTUAL)
ch1.setBusOutputControl(canlib.canDRIVER_NORMAL)
ch1.setBusParams(canlib.canBITRATE_500K)
ch1.busOn()
#sendEgoSpeed(ch1)
#sendLane(ch1)
#sendNextLane(ch1)
#sendNumOfObs(ch1)
sendDataFromCsv(ch1,file_name)
ch1.busOff()