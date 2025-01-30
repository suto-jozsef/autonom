import time
from gps_thread import GPS_Thread
import serial
import RPi.GPIO as GPIO
'''
reset_pin = 23
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(reset_pin, GPIO.OUT)
GPIO.output(reset_pin, GPIO.HIGH)

uart = serial.Serial("/dev/ttyS0", baudrate=4800, bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,
                     stopbits=serial.STOPBITS_ONE, timeout=2)

start = time.time()
while (time.time() - start) < 400:
    inbytes = uart.readline()
    try:
        message = inbytes.decode("utf8")
        #if message[3:6] == 'GGA' or message[3:6] == 'TXT': print('[MESSAGE] {}'.format(message))
        print('[MESSAGE] {}'.format(message))
    except UnicodeDecodeError as e:
        print("Exception")
        pass
    
'''
gps = GPS_Thread(baud=4800)
gps.start()

for i in range(100):
    gpsdatetime = gps.get_date_time()
    position = gps.get_position()
    satellites = gps.get_num_satellites()
    if gpsdatetime is not None: print('[MESSAGE] {}, {}'.format(gpsdatetime, satellites))
    print('[MESSAGE] {}, {}'.format(position[0], position[1]))
    print('[MESSAGES] {}'.format(gps.received_messages))
    time.sleep(1)
gps.stop()
