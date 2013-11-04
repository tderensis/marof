from Adafruit_I2C import Adafruit_I2C

class LSM303DLHC(object):
    """ A combined magnetometer and linear accelerometer. The magnetometer also contains 
    a temperature sensor. Uses the Adafruit_I2C library for the BeagleBone Black.
    
    :param magAddr: the address of the magnetometer
    :param accAddr: the address of the accelerometer
    :param debug: default False, print debug messages
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
    MAG_RATES = (MAG_0_75_HZ, MAG_1_5_HZ, MAG_3_HZ, MAG_7_5_HZ, MAG_15_HZ, 
                 MAG_30_HZ, MAG_75_HZ, MAG_220_HZ)
    
    # Magnetometer measurement ranges
    MAG_RANGE_1_3 = 0b001 << 5 # +-1.3 Gauss, 1100 LSB/Gauss (default)
    MAG_RANGE_1_9 = 0b010 << 5 # +-1.9 Gauss, 855 LSB/Gauss
    MAG_RANGE_2_5 = 0b011 << 5 # +-2.5 Gauss, 670 LSB/Gauss
    MAG_RANGE_4_0 = 0b100 << 5 # +-4.0 Gauss, 450 LSB/Gauss
    MAG_RANGE_4_7 = 0b101 << 5 # +-4.7 Gauss, 400 LSB/Gauss
    MAG_RANGE_5_6 = 0b110 << 5 # +-5.6 Gauss, 330 LSB/Gauss
    MAG_RANGE_8_1 = 0b111 << 5 # +-8.1 Gauss, 230 LSB/Gauss
    MAG_RANGES = {MAG_RANGE_1_3:1100.0, MAG_RANGE_1_9:855.0, MAG_RANGE_2_5:670.0, 
                  MAG_RANGE_4_0:450.0, MAG_RANGE_4_7:400.0, MAG_RANGE_5_6:330.0, 
                  MAG_RANGE_8_1:230.0}
    
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
    ACC_RATES = (ACC_1_HZ, ACC_10_HZ, ACC_25_HZ, ACC_50_HZ, ACC_100_HZ, 
                 ACC_200_HZ, ACC_400_HZ)
    
    # Accelerometer power modes
    ACC_NORMAL_POWER = 0b0 << 3
    ACC_LOW_POWER = 0b1 << 3
    
    # Accelerometer resolution
    ACC_LOW_RES = 0b0 << 3
    ACC_HIGH_RES = 0b1 << 3
    
    # Accelerometer measurement ranges
    ACC_RANGE_2 = 0b00 << 4 # +-2 G, 1 mg/LSB
    ACC_RANGE_4 = 0b01 << 4 # +-4 G, 2 mg/LSB
    ACC_RANGE_8 = 0b10 << 4 # +-8 G, 4 mg/LSB
    ACC_RANGE_16 = 0b11 << 4 # +-16 G, 12 mg/LSB
    ACC_RANGES = {ACC_RANGE_2:1.0, ACC_RANGE_4:2.0, ACC_RANGE_8:4.0, ACC_RANGE_16:12.0}
    
    
    def __init__(self, magAddr, accAddr, debug=False):
        self._debug = debug
        
        # init temperature
        self._tempEnabled = True
        
        # init magnetometer
        self._magEnabled = True
        self._magDataRate = self.MAG_30_HZ
        self._magRange = self.MAG_RANGE_1_3
        self._magnetometer = Adafruit_I2C(magAddr, debug)
        self.enableMagnetometer(self._magEnabled)
        
        # init accelerometer
        self._accEnabled = True
        self._accPowerMode = self.ACC_NORMAL_POWER
        self._accResolution = self.ACC_HIGH_RES
        self._accDataRate = self.ACC_50_HZ
        self._accRange = self.ACC_RANGE_2
        self._accelerometer = Adafruit_I2C(accAddr, debug)
        self.enableAccelerometer(self._accEnabled)
        
        if self._debug:
            print """Magnetometer enabled with 30 Hz refresh rate and +-1.3 Gauss sensitivity.
            Accelerometer enabled in normal power mode with 12-bit resolution, 50 Hz refresh rate, 
            and +-2 G sensitivity. Temperature enabled."""
        
    def enableTemperature(self, enable):
        """ Enable or disable the temperature readings. 
        
        :param enable: If True, enable the temperature readings. If False, disable it.
        """
        self._tempEnabled = enable
        self._writeMagCRA()
    
    def readTemperature(self):
        """ Read the temperature in Celsius.
        
        :returns: the temperature in Celsius
        """
        tl = self._magnetometer.readU8(self._MAG_TEMP_OUT_L_M)
        th = self._magnetometer.readU8(self._MAG_TEMP_OUT_H_M)
        #tl = self._magnetometer.readU8(self._MAG_TEMP_OUT_L_M)
        return self._twos_comp(((th << 8) + tl) >> 4, 12)/8.0 # 12-bit res, left-justified, 8 LSB/C
    
    def setMagnetometerRate(self, hz):
        """ Set the minimum refresh rate of the magnetometer.
        
        :param hz: the data rate should be a MAG_* variable from this class
        """
        assert hz in self.MAG_RATES, "Invalid magnetometer data rate."
        self._magDataRate = hz
        self._writeMagCRA()
    
    def setMagnetometerRange(self, magRange):
        """ Sets the range for the magnetometer.
        
        :param magRange: The range should be one of the MAG_RANGE_* variables from this class.
        """
        assert magRange in self.MAG_RANGES.keys(), "Invalid magnetometer range."
        self._magRange = magRange
        self._writeMagCRB(self)
        
    def enableMagnetometer(self, enable):
        """ Enable or disable the magnetometer. Sets all magnetometer parameters.
        
        :param enable: If True, enable the magnetometer in continuous-conversion mode.
                       If False, put the magnetometer in sleep mode.
        """
        self._magEnabled = enable
        self._writeMagMR()
        self._writeMagCRA()
        self._writeMagCRB()
        
    def readMagnetometer(self):
        """ Read the magnetometer and return Gauss in each direction as a tuple. 
        
        :returns: (mx, my, mz) in Gauss
        """
        # Data pointer is updated automatically after reading each byte from the magnetometer.
        # The data returned goes xh, xl, zh, zl, yh, yl
        data = self._magnetometer.readList(self._MAG_OUT_X_H_M, 6)

        # Convert to 2s complement and convert to Gauss. Has 12-bit resolution, right justified.
        lsbPerGauss = self.MAG_RANGES[self._magRange]
        mx = self._twos_comp(((data[0] & 0x0F) << 8) + data[1], 12)/lsbPerGauss
        mz = self._twos_comp(((data[2] & 0x0F) << 8) + data[3], 12)/lsbPerGauss
        my = self._twos_comp(((data[4] & 0x0F) << 8) + data[5], 12)/lsbPerGauss
        return (mx, my, mz)
        
    def enableAccelerometer(self, enable):
        """ Enable the accelerometer and set the accelerometer parameters.
        
        :param enable: If True enable all axes of the accelerometer. If False, disable it.
        """
        self._accEnabled = enable
        self._writeAccReg1()
        self._writeAccReg4()
        
    def setAccDataRate(self, hz):
        """ Set the data rate for the accelerometer.
        
        :param hz: The accelerometer data rate should be a ACC_* variable from this class.
        """
        if hz not in self.ACC_RATES:
            raise Exception("Invalid acceleration data rate.")
        self._accDataRate = hz
        self._writeAccReg1()
        
    def setAccNormalPower(self):
        """ Set the accelerometer mode to normal power. """
        self._accPowerMode = self.ACC_NORMAL_POWER
        self._writeAccReg1()
        
    def setAccLowPower(self):
        """ Set the accelerometer mode to low power. """
        self._accPowerMode = self.ACC_LOW_POWER
        self._writeAccReg1()
        
    def setAccHighRes(self):
        """ Set the accelerometer mode to high resolution. (12-bit) """
        self._accResolution = self.ACC_HIGH_RES
        self._writeAccReg4()
    
    def setAccLowRes(self):
        """ Set the accelerometer mode to low resolution. (10-bit) """
        self._accResolution = self.ACC_LOW_RES
        self._writeAccReg4()
    
    def setAccRange(self, accRange):
        """ Set the accelerometer measurement range.
        
        :param accRange: The range should be one of the ACC_RANGE_* variables from this class.
        """
        assert accRange in self.ACC_RANGES.keys(), "Invalid acceleration range."
        self._accRange = accRange
        self._writeAccReg4()
    
    def readAccelerometer(self):
        """ Read the acceleration in each direction.
        
        :returns: The acceleration in each direction (ax, ay, az) in G, where 1G = 9.8m/s
        """
        axh = self._accelerometer.readU8(self._ACC_OUT_X_H_A)
        axl = self._accelerometer.readU8(self._ACC_OUT_X_L_A)
        ayh = self._accelerometer.readU8(self._ACC_OUT_Y_H_A)
        ayl = self._accelerometer.readU8(self._ACC_OUT_Y_L_A)
        azh = self._accelerometer.readU8(self._ACC_OUT_Z_H_A)
        azl = self._accelerometer.readU8(self._ACC_OUT_Z_L_A)
        
        # Convert to 2s complement and then to mG. 12 or 10-bit resolution, left justified
        res = 12 if self._accResolution == self.ACC_HIGH_RES else 10
        GPerLsb = self.ACC_RANGES[self._accRange]/1000.0
        ax = self._twos_comp(((axh << 8) + axl) >> (16 - res), res) * GPerLsb
        ay = self._twos_comp(((ayh << 8) + ayl) >> (16 - res), res) * GPerLsb
        az = self._twos_comp(((azh << 8) + azl) >> (16 - res), res) * GPerLsb
        return (ax, ay, az)
    
    def _twos_comp(self, val, bits):
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
        return val
    
    def _writeMagCRA(self):
        if self._tempEnabled:
            self._magnetometer.write8(self._MAG_CRA_REG_M, 0x80 | self._magDataRate)
        else:
            self._magnetometer.write8(self._MAG_CRA_REG_M, 0x00 | self._magDataRate)
    
    def _writeMagCRB(self):
        self._magnetometer.write8(self._MAG_CRB_REG_M, self._magRange)
        
    def _writeMagMR(self):
        if self._magEnabled:
            self._magnetometer.write8(self._MAG_MR_REG_M, 0x00) # continuous-conversion mode
        else:
            self._magnetometer.write8(self._MAG_MR_REG_M, 0x02) # sleep mode

    def _writeAccReg1(self):
        if self._accEnabled:
            self._accelerometer.write8(self._ACC_CTRL_REG1_A, 
                                       self._accDataRate | self._accPowerMode | 0x07) # all axes
        else:
            self._accelerometer.write8(self._ACC_CTRL_REG1_A, 0x00)

    def _writeAccReg4(self):
        self._accelerometer.write8(self._ACC_CTRL_REG4_A, self._accResolution | self._accRange)
