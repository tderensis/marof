from random import random

from marof import MarofModuleHandler, getMicroSeconds
from marof.sensor import Sensor
from marof.filter import FirstOrderLpf

from marof_lcm import sensorData_t

class SensorExample(Sensor):
    """ An example sensor to show an implementation. 
    
    :param name: the name of the sensor
    :param updateInterval: the rate at wich the sensor is polled
    :param filt: the filter to use on the sensor data
    """
    
    def __init__(self, name, updateInterval, filt):
        super(SensorExample, self).__init__(name, updateInterval, filt)
        self._data = 0;
        self._channel = self.name
        self._filtChannel = self.name + "_FILTERED"
        
    @property
    def filterInput(self):
        return self._data
        
    def sensorStep(self):
        self._data = 0.5 - random()
            
    def publishUpdate(self):
        msg = sensorData_t()
        msg.time = getMicroSeconds()
        msg.data = self._data
        self.publish(self._channel, msg)
        if self.filter is not None:
            msg.data = self.filterOutput
            self.publish(self._filtChannel, msg)
            
    def handleMessage(self, channel, data):
        """ Handle a config message. """
        print "Got data on channel:", channel
        print "Data:", data
        
        
if __name__ == "__main__":
    T = 1.0/100
    lpf = FirstOrderLpf(cutoff=0.05, samplingInterval=T)
    sensor = SensorExample(name="SENSOR_EXAMPLE", updateInterval=T, filt=lpf)
    handler = MarofModuleHandler(sensor)
    handler.subscribe("CONFIG_MY_SENSOR", sensor.handleMessage)
    handler.startModule() # start module on separate thread (optional, can also be started via LCM)
    handler.start()
