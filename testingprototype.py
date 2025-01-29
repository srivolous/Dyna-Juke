import serial


def readserial(comport, baudrate):

    ser = serial.Serial(comport, baudrate, timeout=0.1)         # 1/timeout is the frequency at which the port is read
    
    while True:
        data = ser.readline().decode().strip()
        #print(f"{data}")
        if data:
            #if(int(data)<500):return 1
            #else:return 0
            return float(data)


if __name__ == '__main__':
    while True:
        dat = readserial('/dev/ttyUSB0', 115200)
        print(dat)
