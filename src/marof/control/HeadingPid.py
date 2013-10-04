from PidController import PidController

class HeadingPid(PidController):
    def __init__(self, kp, ki, kp):
        super(HeadingPid, self).__init__(kp, ki, kp)
        
    