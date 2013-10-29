import struct

from Adafruit_I2C import Adafruit_I2C

class LSM303DLHC(object):
    """ A combined magnetometer and accelerometer. The magnetometer also contains 
    a temperature sensor.
    
    :param magAddr: the address of the magnetometer
    :param accAddr: the address of the accelerometer
    """
    
    # Magnetometer registers
    _MAG_CRA_REG_M = 0x00
    _MAG_CRB_REG_M = 0x01
    _MAG_MR_REG_M = 0x02
    _MAG_OUT_X_H_M = 0x03
    _MAG_OUT_X_L_M = 0x04
    _MAG_OUT_Z_H_M = 0x05
    _MAG_OUT_Z_L_M = 0x06
    _MAG_OUT_Y_H_M = 0x07
    _MAG_OUT_Y_L_M = 0x08
    _MAG_SR_REG_Mg = 0x09
    _MAG_IRA_REG_M = 0x0A
    _MAG_IRB_REG_M = 0x0B
    _MAG_IRC_REG_M = 0x0C
    _MAG_TEMP_OUT_H_M = 0x31
    _MAG_TEMP_OUT_L_M = 0x32
    
    # Magnetometer data rates
    MAG_0_75_HZ = 0b000 << 2 # 0.75 Hz
    MAG_1_5_HZ = 0b001 << 2 # 1.5 Hz
    MAG_3_HZ = 0b010 << 2 # 3.0 Hz
    MAG_7_5_HZ = 0b011 << 2 # 7.5 Hz
    MAG_15_HZ = 0b100 << 2 # 15 Hz (default)
    MAG_30_HZ = 0b101 << 2 # 30 Hz
    MAG_75_HZ = 0b110 << 2 # 75 Hz
    MAG_220_HZ = 0b111 << 2 # 220 Hz
    
    # Magnetometer range
    MAG_RANGE_1_3 = 0b001 << 5 # +-1.3 Gauss, 1100 LSB/Gauss (default)
    MAG_RANGE_1_9 = 0b010 << 5 # +-1.9 Gauss, 855 LSB/Gauss
    MAG_RANGE_2_5 = 0b011 << 5 # +-2.5 Gauss, 670 LSB/Gauss
    MAG_RANGE_4_0 = 0b100 << 5 # +-4.0 Gauss, 450 LSB/Gauss
    MAG_RANGE_4_7 = 0b101 << 5 # +-4.7 Gauss, 400 LSB/Gauss
    MAG_RANGE_5_6 = 0b110 << 5 # +-5.6 Gauss, 330 LSB/Gauss
    MAG_RANGE_8_1 = 0b111 << 5 # +-8.1 Gauss, 230 LSB/Gauss
    
    # Accelerometer registers
    _ACC_CTRL_REG1_A = 0x20 # Data rate and power mode
    _ACC_CTRL_REG2_A = 0x21
    _ACC_CTRL_REG3_A = 0x22
    _ACC_CTRL_REG4_A = 0x23
    _ACC_CTRL_REG5_A = 0x24
    _ACC_CTRL_REG6_A = 0x25
    _ACC_REFERENCE_A = 0x26
    _ACC_STATUS_REG_A = 0x27
    _ACC_OUT_X_L_A = 0x28
    _ACC_OUT_X_H_A = 0x29
    _ACC_OUT_Y_L_A = 0x2A
    _ACC_OUT_Y_H_A = 0x2B
    _ACC_OUT_Z_L_A = 0x2C
    _ACC_OUT_Z_H_A = 0x2D
    _ACC_FIFO_CTRL_REG_A = 0x2E
    _ACC_FIFO_SRC_REG_A = 0x2F
    _ACC_INT1_CFG_A = 0x30
    _ACC_INT1_SOURCE_A = 0x31
    _ACC_INT1_THS_A = 0x32
    _ACC_INT1_DURATION_A = 0x33
    _ACC_INT2_CFG_A = 0x34
    _ACC_INT2_SOURCE_A = 0x35
    _ACC_INT2_THS_A = 0x36
    _ACC_INT2_DURATION_A = 0x37
    _ACC_CLICK_CFG_A = 0x38
    _ACC_CLICK_SRC_A = 0x39
    _ACC_CLICK_THS_A = 0x3A
    _ACC_TIME_LIMIT_A = 0x3B
    _ACC_TIME_LATENCY_A = 0x3C
    _ACC_TIME_WINDOW_A = 0x3D
    
    # Accelerometer data rates
    ACC_1_HZ = 0b0001 << 4
    ACC_10_HZ = 0b0010 << 4
    ACC_25_HZ = 0b0011 << 4
    ACC_50_HZ = 0b0100 << 4
    ACC_100_HZ = 0b0101 << 4
    ACC_200_HZ = 0b0110 << 4
    ACC_400_HZ = 0b0111 << 4
    
    # Accelerometer power modes
    ACC_NORMAL_POWER = 0b0 << 3
    ACC_LOW_POWER = 0b1 << 3
    
    # Accelerometer resolution
    ACC_LOW_RES = 0b0 << 3
    ACC_HIGH_RES = 0b1 << 3
    
    # Accelerometer range
    ACC_RANGE_2 = 0b00 << 4 # +-2 G, 1 mg/LSB
    ACC_RANGE_4 = 0b01 << 4 # +-4 G, 2 mg/LSB
    ACC_RANGE_8 = 0b10 << 4 # +-8 G, 4 mg/LSB
    ACC_RANGE_16 = 0b11 << 4 # +-16 G, 12 mg/LSB
    
    def __init__(self, magAddr, accAddr, debug=False):
        # init magnetometer
        self.magAddr = magAddr
        self.magEnabled = True
        self.magDataRate = self.MAG_15_HZ
        self.magRange = self.MAG_RANGE_1_3
        self._lsbPerGauss = 1100.0
        self.magnetometer = Adafruit_I2C(magAddr, debug)
        self.setMagnetometerGain(self.magGain)
        self.enableMagnetometer(self.magEnabled)
        
        # init accelerometer
        self.accAddr = accAddr
        self.accEnabled = True
        self.accPowerMode = self.ACC_NORMAL_POWER
        self.accResolution = self.ACC_HIGH_RES
        self.accDataRate = self.ACC_10_HZ
        self.accRange = self.ACC_RANGE_2
        self._mgPerLSB = 1.0
        self.accelerometer = Adafruit_I2C(accAddr, debug)
        self.enableAccerometer(self.accEnabled)
        
        # init temperature
        self.tempEnabled = False
        self.tempBit = 0x00
        self.enableTemperature(self.tempEnabled)
        
    def enableTemperature(self, enable):
        """ Enable or disable the temperature readings. 
        
        :param enable: If True, enable the temperature readings. If False, disable.
        """
        if enable:
            self.tempBit = 0x80
        else:
            self.tempBit = 0x00
        self.magnetometer.write8(self._MAG_CRA_REG_M, self.tempBit | self.magDataRate)
        self.tempEnabled = enable
    
    def setMagnetometerRate(self, hz):
        """ Set the minimum refresh rate of the magnetometer.
        
        :param hz: the data rate should be a MAG_RATE_* variable from this class
        """
        self.magDataRate = hz
        self.magnetometer.write8(self._MAG_CRA_REG_M, self.tempBit | self.magDataRate)
    
    def setMagnetometerRange(self, magRange):
        """ Sets the range for the magnetometer, valid values are MAG_RANGE_*.
        
        :param magRange: The range should be one of the MAG_RANGE_* variables in this class
        """
        if magRange == self.MAG_GAIN_1_3:
            self._lsbPerGauss = 1100.0
        elif magRange == self.MAG_GAIN_1_9:
            self._lsbPerGauss = 855.0
        elif magRange == self.MAG_GAIN_2_5:
            self._lsbPerGauss = 670.0
        elif magRange == self.MAG_GAIN_4_0:
            self._lsbPerGauss = 450.0
        elif magRange == self.MAG_GAIN_4_7:
            self._lsbPerGauss = 400.0
        elif magRange == self.MAG_GAIN_5_6:
            self._lsbPerGauss = 330.0
        elif magRange == self.MAG_GAIN_8_1:
            self._lsbPerGauss = 230.0     
        else:
            raise Exception("Invalid magnetic range is set")
        self.magRange = magRange
        self.magnetometer.write8(self._MAG_CRB_REG_M, self.magRange)
        
    def enableMagnetometer(self, enable):
        """ Enable or disable the magnetometer. 
        
        :param enable: If True, enable the magnetometer in continuous-conversion mode.
                       If False, put the magnetometer in sleep mode.
        """
        if enable:
            self.magnetometer.write8(self._MAG_MR_REG_M, 0x00) # continuous-conversion mode
        else:
            self.magnetometer.write8(self._MAG_MR_REG_M, 0x02) # sleep mode
        self.magEnabled = enable
        
    def readMagnetometer(self):
        """ Read the magnetometer and return Gauss in each directon as a tuple. 
        
        :returns: (x, y, z) in Gauss
        """
        # Data pointer is updated automatically after reading each byte from the magnetometer
        data = self.magnetometer.readList(self._MAG_OUT_X_H_M, 6)

        # Convert to 2s complement and convert to Gauss
        x = struct.unpack('h', struct.pack('BB', data[0], data[1]))[0]/self._lsbPerGauss
        z = struct.unpack('h', struct.pack("BB", data[2], data[3]))[0]/self._lsbPerGauss
        y = struct.unpack('h', struct.pack('BB', data[4], data[5]))[0]/self._lsbPerGauss
        return (x, y, z)
        
    def enableAccerometer(self, enable):
        if enable:
            # enable all axes
            self.accelerometer.write8(self._ACC_CTRL_REG1_A, self.accDataRate | self.accPowerMode | 0x07)
            self.accelerometer.write8(self._ACC_CTRL_REG4_A, self.accResolution | self.accRange)
        else:
            self.accelerometer.write8(self._ACC_CTRL_REG1_A, 0x00)
        self.accEnabled = enable
        
    def setAccDataRate(self, dataRate):
        self.accDataRate = dataRate
        self.accelerometer.write8(self._ACC_CTRL_REG1_A, self.accDataRate | self.accPowerMode | 0x07)
        
    def setAccPowerMode(self, mode):
        self.accPowerMode = mode
        self.accelerometer.write8(self._ACC_CTRL_REG1_A, self.accDataRate | self.accPowerMode | 0x07)
        
    def setAccRange(self, accRange):
        if accRange == self.ACC_RANGE_2:
            self._mgPerLSB = 1.0
        elif accRange == self.ACC_RANGE_4:
            self._mgPerLSB = 2.0
        elif accRange == self.ACC_RANGE_8:
            self._mgPerLSB = 4.0
        elif accRange == self.ACC_RANGE_16:
            self._mgPerLSB = 12.0
        else:
            raise Exception("Invalid acceleration range.")
        self.accRange = accRange
        self.accelerometer.write8(self._ACC_CTRL_REG4_A, self.accResolution | self.accRange)
        
    def readAccelerometer(self):
        ax1 = self.accelerometer.readU8(self._ACC_OUT_X_H_A)
        ax2 = self.accelerometer.readU8(self._ACC_OUT_X_L_A)
        ay1 = self.accelerometer.readU8(self._ACC_OUT_Y_H_A)
        ay2 = self.accelerometer.readU8(self._ACC_OUT_Y_L_A)
        az1 = self.accelerometer.readU8(self._ACC_OUT_Z_H_A)
        az2 = self.accelerometer.readU8(self._ACC_OUT_Z_L_A)
        if self.accResolution == self.ACC_HIGH_RES:
            scale = 16 # 12 bit res
        else:
            scale = 64 # 10 bit res
        # convert to 2s complement and then to mg
        ax = struct.unpack('h', struct.pack('BB', ax1, ax2))[0]*self._mgPerLSB/scale
        ay = struct.unpack('h', struct.pack("BB", ay1, ay2))[0]*self._mgPerLSB/scale
        az = struct.unpack('h', struct.pack('BB', az1, az2))[0]*self._mgPerLSB/scale
        return (ax, ay, az)
    