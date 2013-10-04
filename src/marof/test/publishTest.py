
import lcm

from marof_lcm import configModule_t

if __name__ == "__main__":
    l = lcm.LCM()
    msg = configModule_t()
    msg.time = 2
    msg.command = "s"
    l.publish("CONFIG_MY_SENSOR", msg.encode())