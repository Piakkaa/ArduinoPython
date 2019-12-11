import pyfirmata
import matplotlib.pyplot as plt
import time
from datetime import datetime
import pandas as pd

class SharpSensor():
    '''measuring sharp sensor through pyfirmata with arduino uno'''
    def __init__(self, analogue__input_pin = 5, digital_output_pin = 4,usb_port = '/dev/cu.usbserial-14330',verbose = False, samples = 100, error_threshold = 0.05):
        '''start setting up pins and board'''
        ## initialize board
        self.board = pyfirmata.Arduino(usb_port)
        ## start board firmata
        it = pyfirmata.util.Iterator(self.board)
        it.start()
        ## set pins
        self.digital_output_pin = self.board.get_pin('d:{}:o'.format(digital_output_pin))
        self.analog_input_pin = self.board.get_pin('a:{}:i'.format(analogue__input_pin))
        ## set verbosity
        self.verbose = verbose
        ## samples
        self.samples = samples
        ## error threshold
        self.error_threshold = error_threshold
        ## set default write pin to high
        self.digital_output_pin.write(1)
        
    def read_data(self):
        self.digital_output_pin.write(1)
        time.sleep(1)
        raw_data = {'timeStamp':[],'voltage':[],'error':[],'i':[]}
        for i in range(self.samples):
            self.digital_output_pin.write(0)          #Turn on the dust sensor LED by setting digital pin LOW.
            start_time = datetime.now()
            time.sleep(0.00026)
            for _ in range(100):
                current_reading = self.analog_input_pin.read()
                timestamp = (datetime.now()-start_time).microseconds/1000
                if current_reading > self.error_threshold:
                    if self.verbose > 0:
                        print('output is {} V , time between reading is : {} ms'.format(current_reading*5,timestamp))
                    raw_data['timeStamp'].append(timestamp)
                    raw_data['voltage'].append(current_reading*5)
                    raw_data['error'].append(False)
                    raw_data['i'].append(i)
                    break
                else:
                    if self.verbose > 1 :
                        print('output is {} V , time between reading is : {} ms'.format(current_reading*5,timestamp))
                    raw_data['timeStamp'].append(timestamp)
                    raw_data['voltage'].append(current_reading*5)
                    raw_data['error'].append(True)
                    raw_data['i'].append(i)
                time.sleep(0.000005)
            self.digital_output_pin.write(1) 
            time.sleep(0.01)
        self.raw_data = pd.DataFrame(raw_data)
        self.non_error_raw_data = self.raw_data[self.raw_data['error']== 0]
        self.latest_reading = self.non_error_raw_data['voltage'].mean()
        
    def read_datas(self,n = 10):
        readingData = {'time_stamp':[],'reading(V)':[]}
        for _ in range (n):
            sensor.read_data()
            readingData['reading(V)'].append(sensor.latest_reading)
            readingData['time_stamp'].append(datetime.now())
        self.historicalData = pd.DataFrame(readingData).dropna()
        self.meanHistoricalData = self.historicalData['reading(V)'].mean()
        return self.historicalData
    def plot_latest(self):
        self.raw_data.plot(x='timeStamp',y='voltage',kind = 'scatter')
        plt.show()
