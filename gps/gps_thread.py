import time
import serial
import threading

class GPS_Thread:
    def __init__(self, baud=9600):
        self.knot_to_ms = 0.514444444
        self.satellites = None
        self.time = None
        self.date = None
        self.lati = None
        self.longi = None
        self.speed = None
        self.altitude = None
        self.received_messages = 0
        self.uart = serial.Serial("/dev/ttyS0", baudrate=baud, bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE, timeout=1)
        self.capture_thread = threading.Thread(target=self.read_message)
        self.stop_event = threading.Event()
        
    def start(self):
        print("[GPS] starting thread...")
        self.capture_thread.start()
        
    def stop(self):
        print("[GPS] stop thread")
        self.stop_event.set()
        
    def read_message(self):
        inbytes = None
        
        while not self.stop_event.is_set():
            inbytes = self.uart.read_until()
            if inbytes is not None and len(inbytes) > 0:
                if chr(inbytes[0]) == '$' and self.check_crc(inbytes):
                    self.received_messages += 1
                    
                    try:
                        message = inbytes.decode("utf8")
                        message_type = message[3:6]
                        fields = message.split(',')
                        
                        # time
                        if message_type == 'RMC' or message_type == 'GGA':
                            indx = 1
                            if len(fields[indx]) > 5:
                                timestring = fields[indx]
                                hh = int(timestring[0:2])
                                mm = int(timestring[2:4])
                                ss = int(timestring[4:6])
                                self.time = (hh,mm,ss)
                        
                        # date
                        if message_type == 'RMC':
                            indx = 9
                            if len(fields[indx]) > 5:
                                datestring = fields[indx]
                                dd = int(datestring[0:2])
                                mm = int(datestring[2:4])
                                yy = int(datestring[4:6])
                                self.date = (dd,mm,yy)
                        
                        # position
                        if message_type == 'RMC' or message_type == 'GGA':                 
                            indx1 = 3
                            indx2 = 5
                            
                            if message_type == 'GGA':
                                indx1 -= 1
                                indx2 -= 1
                                
                            if len(fields[indx1]) > 1 and len(fields[indx2]) > 1:
                                self.lati = float(fields[indx1])
                                self.longi = float(fields[indx2])
                                
                            if fields[7]:
                                self.speed = (float(fields[7]) * self.knot_to_ms) * 3.6
                        
                        # satellites
                        if message_type == 'GGA':
                            indx = 7
                            if fields[indx]:
                                self.satellites = int(fields[indx])
                                
                        # altitude
                        if message_type == 'GGA':
                            indx = 9
                            if fields[indx]:
                                self.altitude = float(fields[indx])
                                
                        # speed
                        if message_type == 'RMC' or message_type == 'VTG':
                            indx = 7
                            if fields[indx]:
                                if message_type == 'VTG':
                                    self.speed = float(fields[indx])
                                else:
                                    self.speed = (float(fields[indx]) * self.knot_to_ms) * 3.6
                    
                    except UnicodeDecodeError as e:
                        pass
        print("[GPS] thread stopped!")
                        
    def get_num_satellites(self):
        return self.satellites
    
    def get_time(self):   
        return self.time

    def get_position(self):
        return (self.lati, self.longi)

    def get_date(self):
        return self.date
    
    def get_speed(self):
        return self.speed

    def get_date_time(self):
        if self.date is None or self.time is None:
            return None
        else:
            weekday = self.weekday(self.date)
            weekday = weekday if (weekday > 0) else 7
            dt = (2000+self.date[2], self.date[1], self.date[0], weekday, self.time[0], self.time[1], self.time[2], 0)
            return dt
    
    def check_crc(self, inbytes):
        crc = inbytes[1]
        byte = None
        i = 2
        
        while i < len(inbytes):
            byte = inbytes[i]
            if chr(byte) != '*':
                crc = crc ^ byte
                i += 1
            else:
                break
            
        if i + 2 < len(inbytes):
            real_crc = int(inbytes[i+1:i+3].decode("utf8"), 16)
            if real_crc == (crc & 255):
                return True
            else:
                return False
        else:
            return False

    def weekday(self, date):
        yy = date[2]
        mm = date[1]
        dd = date[0]
        month_codes = [0,3,3,6,1,4,6,2,5,0,3,5]
        greg_century_code = 6
        year_code = (yy + int((yy / 4))) % 7
        month_code = month_codes[mm-1]
        weekday_code = year_code + month_code + greg_century_code + dd
        if yy % 4 == 0 and (mm == 1 or mm == 2):
            weekday_code -= 1
        return weekday_code % 7
