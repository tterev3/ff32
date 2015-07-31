
import usb.core
import usb.util

CMD_SET_ADDRESS =       0x10
CMD_GET_ADDRESS =       0x11
CMD_SET_VENDOR =        0x12
CMD_GET_VENDOR =        0x13
CMD_SET_PRODUCT =       0x14
CMD_GET_PRODUCT =       0x15
CMD_SET_SERIAL_NUMBER =     0x16
CMD_GET_SERIAL_NUMBER =     0x17

CMD_SET_DIGITAL_OUTPUT =    0x20
CMD_SET_BLOCK_DIGITAL_OUTPUTS = 0x30
CMD_READ_DIGITAL_INPUT =    0x21
CMD_READ_BLOCK_DIGITAL_INPUTS = 0x31
CMD_SET_PWM_OUTPUT =    0x22
CMD_READ_ANALOG_INPUT =     0x23
CMD_CONFIG_SPI_BUS =    0x24
CMD_WRITE_SPI_BUS =     0x25
CMD_READ_SPI_BUS =      0x26

CMD_CONFIG_I2C_BUS =    0x27
CMD_WRITE_I2C_BUS =     0x28
CMD_READ_I2C_BUS =      0x29
CMD_CONFIG_1WIRE_BUS =  0x2A
CMD_WRITE_1WIRE_BUS =   0x2B
CMD_READ_1WIRE_BUS =    0x2C

CMD_GET_CHIP_INFO =     0x71
TIMEOUT = 100


def validatePin(pin):
    if (pin[0] != "A" and pin[0] != "B"):
        return False#raise "Invalid pin block; must be 'A' or 'B'"
    if (pin[0] == "A"):
        if (pin[1] < 1 or pin[1] > 6):
            return False #raise "Invalid pin number for block A; must be between 1 and 6"
    if (pin[0] == "B"):
        if (pin[1] < 1 or pin[1] > 12):
            return False #raise "Invalid pin number for block B; must be between 1 and 12"
    return True
def validateBlock(pin_block, states):
    #states=int(states)
    if (pin_block != "A" and pin_block != "B"):
        return False#raise "Invalid pin block; must be 'A' or 'B'"
    if (pin_block == "A"):
        if (states < 0 or states > 63):
            return False#raise "Invalid pin states for block A; must be between 0 and 63"
    #if (pin_block == "B"):
        #if (states < 0 or states > 4095):
        #    return False#raise "Invalid pin states for block B; must be between 0 and 4095"
    return True


def initialize():
    global dev
    dev = usb.core.find(idVendor=0x04D8, idProduct=0xF8B9)
    if dev==None:
        raise "Error: No FF32 found"
    dev.set_configuration()

def close():
    global dev
    usb.util.dispose_resources(dev)

def acknowledge():  #quick check to confirm comms using the chip info command
    dat=bytes([CMD_GET_CHIP_INFO])
    dev.write(1, dat, TIMEOUT)
    reply=dev.read(0x81, 64, TIMEOUT)
    if (reply[1]==0x0F and reply[2]==0x0B):
       return True
    else: return False
 

def setPin(pin, state):
    if validatePin(pin):
        dat=bytes([CMD_SET_DIGITAL_OUTPUT, ord(pin[0]), pin[1], state])
        dev.write(1, dat, TIMEOUT)
        reply=dev.read(0x81, 64, TIMEOUT)
        if (reply[0] != 0x0E):
           raise "Error setting pin output"
    else:
        raise "Invalid pin passed to setPin"

def readPin( pin):
    if validatePin(pin):
        dat=bytes([CMD_READ_DIGITAL_INPUT, ord(pin[0]), pin[1]])
        dev.write(1, dat, TIMEOUT)
        reply=dev.read(0x81, 64, TIMEOUT)
        if (reply[0] != CMD_READ_DIGITAL_INPUT):
           raise "Error reading pin"
        return int(reply[1])
    else:
        raise "Invalid pin passed to setPin"

def setBlock(pin_block, bitmask, states):
    if validateBlock(pin_block, states):
        mask_hi = bitmask >> 8
        mask_low = bitmask - (mask_hi << 8)
        states_hi = states >> 8 
        states_low = states - (states_hi << 8)
        dat=bytes([CMD_SET_BLOCK_DIGITAL_OUTPUTS, ord(pin_block), mask_hi, mask_low, states_hi, states_low])
        dev.write(1, dat, TIMEOUT)
        reply=dev.read(0x81, 64, TIMEOUT)
        if (reply[0] != 0x0E):
           raise "Error setting pin output"
    else:
        raise "Invalid pin passed to setBlock"
    
def readBlock(pin_block, bitmask):
    mask_hi = bitmask >> 8
    mask_low = bitmask - (mask_hi << 8)
    dat=bytes([CMD_READ_BLOCK_DIGITAL_INPUTS, ord(pin_block), mask_hi, mask_low])
    dev.write(1, dat, TIMEOUT)
    reply=dev.read(0x81, 64, TIMEOUT)
    if (reply[0] != CMD_READ_BLOCK_DIGITAL_INPUTS):
        raise "Error reading digital inputs"
    value = int(reply[1] * 256 + reply[2])
    return value

def setPWM(pin, duty_cycle):
    if validatePin(pin) and pin[0]=='A':
        dat=bytes([CMD_SET_PWM_OUTPUT, ord(pin[0]), pin[1], duty_cycle])
        dev.write(1, dat, TIMEOUT)
        reply=dev.read(0x81, 64, TIMEOUT)
        if (reply[0] != 0x0E):
           raise "Error setting PWM output"
    else:
        raise "Invalid pin passed to setPWM"

def readAnalog(pin):
    if validatePin(pin) and pin[0]=='B':
        dat=bytes([CMD_READ_ANALOG_INPUT, ord(pin[0]), pin[1]])
        dev.write(1, dat, TIMEOUT)
        reply=dev.read(0x81, 64, TIMEOUT)
        if (reply[0] != CMD_READ_ANALOG_INPUT):
           raise "Error reading analog pin"
        vcc = int(reply[1])
        value = int(reply[2] * 256 + reply[3])
        return (vcc, value)
    else:
        raise "Invalid pin passed to readAnalog"


def setSPIPins(cs_pin, sck_pin, mosi_pin, miso_pin):
    if validatePin(cs_pin) and validatePin(sck_pin) and validatePin(mosi_pin) and validatePin(miso_pin):
        cs_pin_block=ord(cs_pin[0])
        cs_pin_num=cs_pin[1]
        sck_pin_block=ord(sck_pin[0])
        sck_pin_num=sck_pin[1]
        mosi_pin_block=ord(mosi_pin[0])
        mosi_pin_num=mosi_pin[1]
        miso_pin_block=ord(miso_pin[0])
        miso_pin_num=miso_pin[1]
        dat=bytes([CMD_CONFIG_SPI_BUS, cs_pin_block, cs_pin_num, sck_pin_block, sck_pin_num, mosi_pin_block, mosi_pin_num, miso_pin_block, miso_pin_num])
        dev.write(1, dat, TIMEOUT)
        reply=dev.read(0x81, 64, TIMEOUT)
        if (reply[0] != 0x0E):
           raise "Error setting SPI pins"
    else:
        raise "Invalid pin passed to setSPIPins"

def writeSPI(data):
    if (len(data) > 60):
        raise "Error writing SPI data; write data length > 60 bytes"
    dat=bytes([CMD_WRITE_SPI_BUS, len(data)])
    dat+=bytes(data)
    dev.write(1, dat, TIMEOUT)
    reply=dev.read(0x81, 64, TIMEOUT)
    if (reply[0] != 0x0E):
       raise "Error writing SPI data"    

def readSPI(read_len, data):
    if (read_len > 60):
        raise "Error writing SPI data; read data length > 60 bytes"
    if (len(data) > 60):
        raise "Error writing SPI data; write data length > 60 bytes"
    dat=bytes([CMD_READ_SPI_BUS, len(data), read_len-1])
    dat+=bytes(data)
    dev.write(1, dat, TIMEOUT)
    reply=dev.read(0x81, 64, TIMEOUT)
    if (reply[0] != CMD_READ_SPI_BUS):
       raise "Error writing SPI data"  
    return list(reply[2:(read_len+2)])

def setI2CPins(scl_pin, sda_pin):
    if validatePin(scl_pin) and validatePin(sda_pin):
        scl_pin_block=ord(scl_pin[0])
        scl_pin_num=scl_pin[1]
        sda_pin_block=ord(sda_pin[0])
        sda_pin_num=sda_pin[1]
        dat=bytes([CMD_CONFIG_I2C_BUS, scl_pin_block, scl_pin_num, sda_pin_block, sda_pin_num])
        reply=dev.read(0x81, 64, TIMEOUT)
        if (reply[0] != 0x0E):
           raise "Error setting I2C pins"
    else:
        raise "Invalid pin passed to setI2CPins"

def writeI2C(data):
    if (len(data) > 60):
        raise "Error writing I2C data; write data length > 60 bytes"
    dat=bytes([CMD_WRITE_I2C_BUS, len(data)])
    dat+=bytes(data)
    dev.write(1, dat, TIMEOUT)
    reply=dev.read(0x81, 64, TIMEOUT)
    if (reply[0] != 0x0E):
       raise "Error writing I2C data"    

def readI2C(read_len, data):
    if (read_len > 60):
        raise "Error writing I2C data; read data length > 60 bytes"
    if (len(data) > 60):
        raise "Error writing I2C data; write data length > 60 bytes"
    dat=bytes([CMD_READ_I2C_BUS, len(data), read_len-1])
    dat+=bytes(data)
    dev.write(1, dat, TIMEOUT)
    reply=dev.read(0x81, 64, TIMEOUT)
    if (reply[0] != CMD_READ_I2C_BUS):
       raise "Error writing I2C data"    
    return list(reply[2:(read_len+2)])

def writeByteI2C(addr, byte):
    addr = addr * 2
    dat = bytes([addr, byte])
    writeI2C(dat)

def writeBlockI2C(addr, data):
    addr = addr * 2
    dat = bytes([addr])
    dat += bytes(data)
    writeI2C(dat)

def readByteI2C( addr):
    addr = (addr * 2) + 1
    dat = bytes([addr])
    reply = readI2C(1, dat)
    return reply[0]

def readWordI2C(addr):
    addr = (addr * 2) + 1
    dat = bytes([addr])
    reply = readI2C(2, dat)
    little_byte = reply[0]
    big_byte = reply[1]
    word = big_byte * 256 + little_byte
    return word

def readBlockI2C(addr, read_len):
    addr = (addr * 2) + 1
    dat = bytes([addr])
    reply = readI2C(read_len, dat)
    return list(reply[0:read_len])


