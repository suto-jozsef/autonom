import time
import serial

class L80:
    def __init__(self, baud=9600, verbose=False):
        self.verbose = verbose
        self.uart = serial.Serial("/dev/ttyS0", baudrate=baud, bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE, timeout=1)
        
    
    def get_num_satellites(self):
        '''GGA message 7th field'''
        fields = self.read_message(mess_type='GGA', timeout=5.0)
        idx = 7
        if fields is not None:
            satelites = int(fields[idx])
            if self.verbose: print('[INFO] Satelites in view: {}'.format(satelites))
            return satelites
        else:
            return 0
    
    def get_status(self):
        '''GGA message 6th field'''
        idx = 6
        fields = self.read_message(mess_type='GGA', timeout=5.0)
        if fields is not None:
            quality = int(fields[idx])
            if self.verbose: print('[INFO] GPS quality: {}'.format(quality))
            return quality
        else:
            return None
    
    def get_utc_time(self, from_gga=True):
        idx = 1
        if from_gga:
            fields = self.read_message(mess_type='GGA', timeout=5.0)
        else:
            fields = self.read_message(mess_type='RMC', timeout=5.0)
        if fields is not None and len(fields[idx]) > 5:
            timestring = fields[idx]
            hh = int(timestring[0:2])
            mm = int(timestring[2:4])
            ss = int(timestring[4:6])
            if self.verbose: print('[INFO] Time: {}:{}:{}'.format(hh,mm,ss))
            return (hh,mm,ss)
        else:
            return None
        
    def get_position(self, from_gga=True):
        lati_idx = 2
        longi_idx = 4
        if from_gga:
            fields = self.read_message(mess_type='GGA', timeout=5.0)
        else:
            fields = self.read_message(mess_type='RMC', timeout=5.0)
            lati_idx += 1
            longi_idx += 1
        if fields is not None:
            latitude = float(fields[lati_idx])
            longitude = float(fields[longi_idx])
            if self.verbose: print('[INFO] Lati and longitude: {},{}'.format(latitude,longitude))
            return (latitude, longitude)
        else:
            return None

    def get_date(self):
        fields = self.read_message(mess_type='RMC', timeout=5.0)
        idx = 9
        if fields is not None and len(fields[idx]) > 5:
            datestring = fields[idx]
            dd = int(datestring[0:2])
            mm = int(datestring[2:4])
            yy = int(datestring[4:6])
            if self.verbose: print('[INFO] Date: {}/{}/{}'.format(dd,mm,yy))
            return (dd,mm,yy)
        else:
            return None

    def get_date_time(self):
        date = self.date()
        utc = self.utc()
        if date is None or utc is None:
            return None
        else:
            weekday = self.weekday(date)
            weekday = weekday if (weekday > 0) else 7
            dt = (2000+date[2], date[1], date[0], weekday, utc[0], utc[1], utc[2], 0)
            if self.verbose: print('[INFO] Date and time: {}'.format(dt))
            return dt
    
    def read_message(self, mess_types, timeout=1.0):
        inbytes = None
        start = time.time()
        while (time.time() - start) < timeout:
            inbytes = self.uart.read_until()
            if inbytes is not None:
                if chr(inbytes[0]) == '$' and inbytes[3:6].decode("utf8") == mess_type \
                and self.check_crc(inbytes):
                    break
        if inbytes is not None:
            message = inbytes.decode("utf8")
            if self.verbose: print('[MESSAGE] {}'.format(message))
            fields = message.split(',')
            return fields
        else:
            print('[ERROR] Timeout without GPS message!')
            return None

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
                if self.verbose: print('[ERROR] Wrong CRC!')
                return False
        else:
            if self.verbose: print('[ERROR] Missing CRC!')
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