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
        
    @property
    def filterInput(self):
        return self._data
        
    def sensorStep(self):
        self._data = 0.5 - random()
            
    def publishUpdate(self):
        msg = sensorData_t()
        msg.time = getMicroSeconds()
        msg.data = self._data
        self.publish(self.name, msg)
        msg.data = self.filterOutput
        self.publish(self.name+"_FILTERED", msg)
            
    def handleMessage(self, channel, data):
        """ Handle a config message. """
        print "Got data on channel:", channel
        print "Data:", data
        
        
if __name__ == "__main__":
    lpf = FirstOrderLpf(cutoff=0.5, samplingInterval=0.1)
    sensor = SensorExample(name="SENSOR_EXAMPLE", updateInterval=0.1, filt=lpf)
    handler = MarofModuleHandler(sensor)
    handler.subscribe("CONFIG_MY_SENSOR", sensor.handleMessage)
    handler.start()
    sensor.start()
