from Adafruit_I2C import Adafruit_I2C

class L3GD20(object):
    """ A 3 axis gyroscope that measures angular rate. Includes a low-pass filter. 
    Uses the Adafruit_I2C library for the BeagleBone Black
    
    :param gyroAddr: the address of the gyroscope
    :param debug: default False, print debug messages
    """
    # Gyroscope registers
    _WHO_AM_I = 0x0F
    _CTRL_REG1 = 0x20
    _CTRL_REG2 = 0x21
    _CTRL_REG3 = 0x22
    _CTRL_REG4 = 0x23
    _CTRL_REG5 = 0x24
    _REFERENCE = 0x25
    _OUT_TEMP = 0x26
    _STATUS_REG = 0x27
    _OUT_X_L = 0x28
    _OUT_X_H = 0x29
    _OUT_Y_L = 0x2A
    _OUT_Y_H = 0x2B
    _OUT_Z_L = 0x2C
    _OUT_Z_H = 0x2D
    _FIFO_CTRL_REG = 0x2E
    _FIFO_SRC_REG = 0x2F
    _INT1_CFG = 0x30
    _INT1_SRC = 0x31
    _INT1_THS_XH = 0x32
    _INT1_THS_XL = 0x33
    _INT1_THS_YH = 0x34
    _INT1_THS_YL = 0x35
    _INT1_THS_ZH = 0x36
    _INT1_THS_ZL = 0x37
    _INT1_DURATION = 0x38
    
    # Gyroscope data rates
    DR_95_HZ = 0b00 << 6
    DR_190_HZ = 0b01 << 6
    DR_380_HZ = 0b10 << 6
    DR_760_HZ = 0b11 << 6
    DATA_RATES = (DR_95_HZ, DR_190_HZ, DR_380_HZ,  DR_760_HZ)
    
    # Gyroscope bandwidth (varies with data rate)
    BW_1 = 0b00 << 4 # DR_95_HZ: 12.5, DR_190_HZ: 12.5, DR_380_HZ: 20,  DR_760_HZ: 30
    BW_2 = 0b01 << 4 # DR_95_HZ: 25,   DR_190_HZ: 25,   DR_380_HZ: 25,  DR_760_HZ: 35
    BW_3 = 0b10 << 4 # DR_95_HZ: 25,   DR_190_HZ: 50,   DR_380_HZ: 50,  DR_760_HZ: 50
    BW_4 = 0b11 << 4 # DR_95_HZ: 25,   DR_190_HZ: 70,   DR_380_HZ: 100, DR_760_HZ: 100
    BANDWIDTHS = (BW_1, BW_2, BW_3, BW_4)
    
    # Gyroscope ranges (sensitivity)
    RANGE_250 = 0b00 << 4 # +-250 deg/s, 8.75 mdps/digit 
    RANGE_500 = 0b01 << 4 # +-500 deg/s, 17.5 mdps/digit 
    RANGE_2000 = 0b10 << 4 # +-2000 deg/s, 70 mdps/digit 
    RANGES = {RANGE_250:8.75, RANGE_500:17.5, RANGE_2000:70}
    
    
    def __init__(self, gyroAddr, debug=False):
        self._debug = debug
        self._gyroEnabled = True
        self._gyroRange = self.RANGE_250
        self._gyroDataRate = self.DR_95_HZ
        self._gyroBW = self.BW_1
        self._gyro = Adafruit_I2C(gyroAddr, debug)
        self.enableGyroscope(self._gyroEnabled)
        if self._debug:
            print """Enabled gyroscope with 95 Hz refresh rate, +-250 degrees/sec sensitivity, and 
            low-pass filter with cutoff of 12.5 Hz."""
        
    def enableGyroscope(self, enable):
        """ Enable or disable the gyroscope.
        
        :param enable: If True, enable the gyroscope in continuous-conversion mode.
                       If False, put the gyroscope in power down.
        """
        self.gyroEnabled = enable
        self._writeReg1()
        self._writeReg4()
        
    def setGyroBW(self, bw):
        """ Set the bandwidth for the gyroscope.
        
        :param bw: The bandwidth should be a BW_* variable from this class.
        """
        assert bw in self.BANDWIDTHS, "Invalid gyro bandwidth."
        self._gyroBW = bw
        self._writeReg1()
        
    def setGyroDataRate(self, hz):
        """ Set the data rate for the gyroscope.
        
        :param hz: The gyroscope data rate should be a DR_* variable from this class.
        """
        assert hz in self.DATA_RATES, "Invalid gyro bandwidth"
        self._gyroDataRate = hz
        self._writeReg1()
        
    def setGyroRange(self, gyroRange):
        """ Set the range\sensitivity of the gyroscope.
        
        :param gyroRange: The range should be a RANGE_* variable from this class.
        """
        assert gyroRange in self.RANGES.keys(), "Invalid gyro range."
        self._gyroRange = gyroRange
        self._writeReg4()
        
    def readGyroscope(self):
        """ Read the gyroscope and return degrees/sec about each axis. 
        
        :returns: (gx, gy, gz) in degrees/sec
        """
        gxl = self._gyro.readU8(self._OUT_X_L)
        gxh = self._gyro.readU8(self._OUT_X_H)
        gyl = self._gyro.readU8(self._OUT_Y_L)
        gyh = self._gyro.readU8(self._OUT_Y_H)
        gzl = self._gyro.readU8(self._OUT_Z_L)
        gzh = self._gyro.readU8(self._OUT_Z_H)
        
        # Convert to 2s complement and then to mG. 16-bit resolution
        mdPerLsb = self.RANGES[self._gyroRange]
        gx = self._twos_comp((gxh << 8) + gxl, 16) * mdPerLsb/1000.0
        gy = self._twos_comp((gyh << 8) + gyl, 16) * mdPerLsb/1000.0
        gz = self._twos_comp((gzh << 8) + gzl, 16) * mdPerLsb/1000.0
        return (gx, gy, gz)
    
    def _twos_comp(self, val, bits):
        if (val&(1<<(bits-1))) != 0:
            val = val - (1<<bits)
        return val
    
    def _writeReg1(self):
        if self._gyroEnabled:
            self._gyro.write8(self._CTRL_REG1, self._gyroDataRate | self._gyroBW | 0x0F)
        else:
            self._gyro.write8(self._CTRL_REG1, 0x00)

    def _writeReg4(self):
        self._gyro.write8(self._CTRL_REG4, self._gyroRange)
