from random import random

from marof import MarofModuleHandler, getMicroSeconds
from marof.sensor import Sensor
from marof.filter import SimpleLpf

from marof_lcm import sensorData_t

class SensorExample(Sensor):
    """ An example sensor to show an example implementation. """
    
    def __init__(self, name, updateInterval, filt):
        super(SensorExample, self).__init__(name, updateInterval, filt)
        self._data = 0;
        self._filteredData = 0;
        
    def sensorStep(self):
        #print "Doing sensor step..."
        r = random()
        self._data = self._data - 0.5 + r
        
    def applyFilter(self):
        if self.filter is not None:
            self._filteredData = self.filter.step(self._data)
            
    def publishUpdate(self):
        msg = sensorData_t()
        msg.time = getMicroSeconds()
        msg.data = self._data
        self.publish(self.name, msg)
        msg.data = self._filteredData
        self.publish(self.name+"_FILTERED", msg)
            
    def handleMessage(self, channel, data):
        print "Got data on channel:", channel
        print "Data:", data
        
        
if __name__ == "__main__":
    lpf = SimpleLpf(0.9)
    sensor = SensorExample(name="SENSOR_EXAMPLE", updateInterval=0.1, filt=lpf)
    handler = MarofModuleHandler(sensor)
    handler.subscribe("CONFIG_MY_SENSOR", sensor.handleMessage)
    handler.start()
    sensor.start()
