import time
import lcm

from marof_lcm import motorCommand_t
from marof import getMicroSeconds

if __name__ == "__main__":
    
    l = lcm.LCM()
    msg = motorCommand_t()
    msg.speedPercent = 50
    msg.turnPercent = 0
    msg.time = getMicroSeconds
    l.publish("MOTOR", msg.encode())
    time.sleep(2)
    
    msg.speedPercent = -50
    msg.turnPercent = 0
    msg.time = getMicroSeconds
    l.publish("MOTOR", msg.encode())
    time.sleep(2)
    
    msg.speedPercent = 0
    msg.turnPercent = 50
    msg.time = getMicroSeconds
    l.publish("MOTOR", msg.encode())
    time.sleep(2)
   
    msg.speedPercent = 0
    msg.turnPercent = -50
    msg.time = getMicroSeconds
    l.publish("MOTOR", msg.encode())
    time.sleep(2)