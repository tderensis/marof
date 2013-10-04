
from marof import MarofModule, MarofModuleHandler, getMicroSeconds

from marof_lcm import sensorData_t

class SensorExample(MarofModule):
    """ An example sensor to show an example implementation. """
    
    def __init__(self, name, updateInterval):
        super(SensorExample, self).__init__(name, updateInterval)
        self._data = 0;
        
    
    def publishUpdate(self):
        #print "Publishing update..."
        msg = sensorData_t()
        msg.time = getMicroSeconds()
        msg.data = self._data
        self.lcmTX.publish(self.name, msg.encode())
        
    def step(self):
        #print "Doing sensor step..."
        self._data = self._data + 1;
        
        
    def handleMessage(self, channel, data):
        print "Got data on channel:", channel
        print "Data:", data
        

if __name__ == "__main__":
    sensor = SensorExample(name="SENSOR_EXAMPLE", updateInterval=0.1)
    handler = MarofModuleHandler(sensor)
    handler.subscribe("CONFIG_MY_SENSOR", sensor.handleMessage)
    handler.start()
    sensor.start()