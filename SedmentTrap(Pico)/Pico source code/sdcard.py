"""
MicroPython driver for SD cards using SPI bus.

Requires an SPI bus and a CS pin.  Provides readblocks and writeblocks
methods so the device can be mounted as a filesystem.

Example usage on pyboard:

    import pyb, sdcard, os
    sd = sdcard.SDCard(pyb.SPI(1), pyb.Pin.board.X5)
    pyb.mount(sd, '/sd2')
    os.listdir('/')

Example usage on ESP8266:

    import machine, sdcard, os
    sd = sdcard.SDCard(machine.SPI(1), machine.Pin(15))
    os.mount(sd, '/sd')
    os.listdir('/')


The followings are modified on Sep., 2020 by ManDorl:

5. init_card_v2 scheme is changed.
   - set CCS 1 to support HC SD card by issuing ACMD41
   - wait for ready
   - check whether CCS is set by reading OCR
     . if CCS is set, set cdv to 1
     . else set cdv to 512

4. cs is now to be int or Pin object

   sd = SDCard(spi, cs=5) 
   # or
   sd = SDCard(spi, cs=Pin(5))

3. crc7 is generated at the runtime

2. one dummy 0xff is transferred before with cmds

1. the method of calculating the total sector number
   is changed to meet the CSD v1.0 spec requirement

0 and something more...

Currently 2GB, 8GB and 16GB SD Cards are supported.
"""
from micropython import const
import time


_CMD_TIMEOUT = const(100)

_R1_IDLE_STATE = const(1 << 0)
# R1_ERASE_RESET = const(1 << 1)
_R1_ILLEGAL_COMMAND = const(1 << 2)
# R1_COM_CRC_ERROR = const(1 << 3)
# R1_ERASE_SEQUENCE_ERROR = const(1 << 4)
# R1_ADDRESS_ERROR = const(1 << 5)
# R1_PARAMETER_ERROR = const(1 << 6)
_TOKEN_CMD25 = const(0xFC)
_TOKEN_STOP_TRAN = const(0xFD)
_TOKEN_DATA = const(0xFE)


class SDCard:
    def __init__(self, spi, cs, baudrate=400000):
        self.spi = spi
        if isinstance(cs, int):
            from machine import Pin
            self.cs = Pin(cs)
            del Pin
        else:
            self.cs = cs
        self.baudrate = baudrate

        self.cmdbuf = bytearray(7)
        self.dummybuf = bytearray(512)
        self.tokenbuf = bytearray(1)
        for i in range(512):
            self.dummybuf[i] = 0xFF
        self.dummybuf_memoryview = memoryview(self.dummybuf)

        # initialise the card
        self.init_card()

    def __str__(self):
        cs = str(self.cs) 
        cs = cs[cs.index('(') + 1 : cs.index(')')]  # leave only number in 'Pin(number)'
        return 'SDCard(spi, cs=%s, baudrate=%d)\n  spi: %s' % (cs, self.baudrate, str(self.spi))
 
    def __repr__(self):
        return self.__str__()
 
    def init_spi(self, baudrate):
        try:
            master = self.spi.MASTER
        except AttributeError:
            # on ESP8266
            self.spi.init(baudrate=baudrate, phase=0, polarity=0)
        else:
            # on pyboard
            self.spi.init(master, baudrate=baudrate, phase=0, polarity=0)

    def init_card(self):
        # init CS pin
        self.cs.init(self.cs.OUT, value=1)

        # init SPI bus; use low data rate for initialisation
        self.init_spi(400000)

        # clock card at least 100 cycles with cs high
        for i in range(16):
            self.spi.write(b"\xff")

        # CMD0: init card; should return _R1_IDLE_STATE (allow 5 attempts)
        for _ in range(5):
            if self.cmd(0, 0, 0x95) == _R1_IDLE_STATE:
                break
            else:
                raise OSError("no SD card")

        # CMD8: determine card version
        MAX_RETRY = 1
        for retry in range(MAX_RETRY + 1):
            # 0001b : 2.7=3.6V
            # 0xAA  : check pattern
            r = self.cmd(8, 0x01AA, 0x87, 4)
            if r == _R1_IDLE_STATE:
                self.init_card_v2()
                break
            elif r == (_R1_IDLE_STATE | _R1_ILLEGAL_COMMAND):
                self.init_card_v1()
                break
            else:
                print('CMD8 error %d' % retry)
                if retry == MAX_RETRY:
                    raise OSError("couldn't determine SD card version: 0x%02x" % r)

        # get the number of sectors
        # CMD9: response R2 (R1 byte + 16-byte block read)
        if self.cmd(9, 0, 0, 0, False) != 0:
            raise OSError("no response from SD card")
        csd = bytearray(16)
        self.readinto(csd)
        if csd[0] & 0xC0 == 0x40:  # CSD version 2.0
            self.sectors = ((csd[8] << 8 | csd[9]) + 1) * 1024
        elif csd[0] & 0xC0 == 0x00:  # CSD version 1.0 (old, <=2GB)
            self.block_len = 2 ** (csd[5] & 0x0f)  # READ_BL_LEN [83:80]
            c_size = ((csd[6] & 0b11) << 10) | (csd[7] << 2) | ((csd[8] & 0b11000000) >> 6)
            c_size_mult = ((csd[9] & 0b11) << 1) | csd[10] >> 7
            self.sectors = (c_size + 1) * (2 ** (c_size_mult + 2)) * int(self.block_len / 512)
            # print("c_size: %d c_size_mult: %d sectors: %d" % (c_size, c_size_mult, self.sectors))

            # Address is in byte units in Standard Capacity SD Card
            #            in block (512 Bytes) units in a High Capacity SD
            #
            # For CSD v1.0 set address in byte units: 
            # self.cdv = 512 <- solved with OCR register!!!

        else:
            raise OSError("SD card CSD format not supported")
        # print('sectors', self.sectors)

        # CMD16: set block length to 512 bytes
        if self.cmd(16, 512, 0) != 0:
            raise OSError("can't set 512 block size")

        # set to high data rate now that it's initialised
        self.init_spi(self.baudrate)

    def init_card_v1(self):
        for i in range(_CMD_TIMEOUT):
            self.cmd(55, 0, 0)
            if self.cmd(41, 0, 0) == 0:
                self.cdv = 512
                # print("[SDCard] v1 card")
                return
        raise OSError("timeout waiting for v1 card")

    def init_card_v2(self):
        TE = True
        for i in range(_CMD_TIMEOUT):
            time.sleep_ms(50)
            # CMD58 is optional before issuing ACMD41, so not send
            # set CSS to '1' to support High Capacity SD Card
            self.cmd(55, 0, 0)
            if self.cmd(41, 0x40000000, 0) == 0:    # ready?
                # check whether CCS is set or not by reading OCR
                # Format R3: R1 + OCR 4 bytes 
                if self.cmd(58, 0, 0, 0, False) == 0:
                    ocr = bytearray(4)
                    self.spi.readinto(ocr, 0xff)

                    # print('CMD58 OCR[3]=0x02x' % ocr[0])  # big endian format
                    if ocr[0] & 0x80:
                        self.cdv = 1 if (ocr[0] & 0x40) else 512

                        # print("[SDCard] v2 card")
                        TE = False
                        break

        # release SPI
        self.cs(1)
        self.spi.write(b"\xff")

        if TE:
            raise OSError("timeout waiting for v2 card")
        else:
            return


    """
    # CRC7 generation function:

    CRC7_POLY = 0x89
    for i in range(256):
        CRC7[i] = i ^ CRC7_POLY if (i & 0x80) else i 
        for bit in range(1, 8):
            CRC7[i] <<= 1
            if CRC7[i] & 0x80:
                CRC7[i] ^= CRC7_POLY
        CRC7[i] &= 0x7F

    # Refer to:
    #   https://electronics.stackexchange.com/questions/321304/how-to-use-the-data-crc-of-sd-cards-in-spi-mode
    #   https://github.com/hazelnusse/crc7/blob/master/crc7.cc
    """
    CRC7 = [
        0x00, 0x09, 0x12, 0x1b, 0x24, 0x2d, 0x36, 0x3f, 0x48, 0x41, 0x5a, 0x53, 0x6c, 0x65, 0x7e, 0x77,
        0x19, 0x10, 0x0b, 0x02, 0x3d, 0x34, 0x2f, 0x26, 0x51, 0x58, 0x43, 0x4a, 0x75, 0x7c, 0x67, 0x6e,
        0x32, 0x3b, 0x20, 0x29, 0x16, 0x1f, 0x04, 0x0d, 0x7a, 0x73, 0x68, 0x61, 0x5e, 0x57, 0x4c, 0x45,
        0x2b, 0x22, 0x39, 0x30, 0x0f, 0x06, 0x1d, 0x14, 0x63, 0x6a, 0x71, 0x78, 0x47, 0x4e, 0x55, 0x5c,
        0x64, 0x6d, 0x76, 0x7f, 0x40, 0x49, 0x52, 0x5b, 0x2c, 0x25, 0x3e, 0x37, 0x08, 0x01, 0x1a, 0x13,
        0x7d, 0x74, 0x6f, 0x66, 0x59, 0x50, 0x4b, 0x42, 0x35, 0x3c, 0x27, 0x2e, 0x11, 0x18, 0x03, 0x0a,
        0x56, 0x5f, 0x44, 0x4d, 0x72, 0x7b, 0x60, 0x69, 0x1e, 0x17, 0x0c, 0x05, 0x3a, 0x33, 0x28, 0x21,
        0x4f, 0x46, 0x5d, 0x54, 0x6b, 0x62, 0x79, 0x70, 0x07, 0x0e, 0x15, 0x1c, 0x23, 0x2a, 0x31, 0x38,
        0x41, 0x48, 0x53, 0x5a, 0x65, 0x6c, 0x77, 0x7e, 0x09, 0x00, 0x1b, 0x12, 0x2d, 0x24, 0x3f, 0x36,
        0x58, 0x51, 0x4a, 0x43, 0x7c, 0x75, 0x6e, 0x67, 0x10, 0x19, 0x02, 0x0b, 0x34, 0x3d, 0x26, 0x2f,
        0x73, 0x7a, 0x61, 0x68, 0x57, 0x5e, 0x45, 0x4c, 0x3b, 0x32, 0x29, 0x20, 0x1f, 0x16, 0x0d, 0x04,
        0x6a, 0x63, 0x78, 0x71, 0x4e, 0x47, 0x5c, 0x55, 0x22, 0x2b, 0x30, 0x39, 0x06, 0x0f, 0x14, 0x1d,
        0x25, 0x2c, 0x37, 0x3e, 0x01, 0x08, 0x13, 0x1a, 0x6d, 0x64, 0x7f, 0x76, 0x49, 0x40, 0x5b, 0x52,
        0x3c, 0x35, 0x2e, 0x27, 0x18, 0x11, 0x0a, 0x03, 0x74, 0x7d, 0x66, 0x6f, 0x50, 0x59, 0x42, 0x4b,
        0x17, 0x1e, 0x05, 0x0c, 0x33, 0x3a, 0x21, 0x28, 0x5f, 0x56, 0x4d, 0x44, 0x7b, 0x72, 0x69, 0x60,
        0x0e, 0x07, 0x1c, 0x15, 0x2a, 0x23, 0x38, 0x31, 0x46, 0x4f, 0x54, 0x5d, 0x62, 0x6b, 0x70, 0x79]


    def crc7(self, cmds, length=5, offset=0):
        crc = 0
        for i in range(length):
            crc = self.CRC7[(cmds[i + offset] ^ (crc << 1)) & 0xff]
        crc = (crc << 1) | 0x01
        return crc

    def cmd(self, cmd, arg, crc, final=0, release=True, skip1=False):
        self.cs(0)

        # create and send the command
        buf = self.cmdbuf
        buf[0] = 0xFF
        buf[1] = 0x40 | cmd
        buf[2] = (arg >> 24) & 0xff
        buf[3] = (arg >> 16) & 0xff
        buf[4] = (arg >>  8) & 0xff
        buf[5] = arg & 0xff
        buf[6] = self.crc7(buf, offset=1)
        # buf[5] = crc

        self.spi.write(buf)

        if skip1:
            self.spi.readinto(self.tokenbuf, 0xFF)

        # wait for the response (response[7] == 0)
        for i in range(_CMD_TIMEOUT):
            self.spi.readinto(self.tokenbuf, 0xFF)
            response = self.tokenbuf[0]
            if not (response & 0x80):
                # this could be a big-endian integer that we are getting here
                for j in range(final):
                    self.spi.write(b"\xff")

                if release:
                    self.cs(1)
                    self.spi.write(b"\xff")

                return response

        # timeout
        self.cs(1)
        self.spi.write(b"\xff")
        return -1

    def readinto(self, buf):
        self.cs(0)

        # read until start byte (0xff)
        for i in range(_CMD_TIMEOUT):
            self.spi.readinto(self.tokenbuf, 0xFF)
            if self.tokenbuf[0] == _TOKEN_DATA:
                break
        else:
            self.cs(1)
            raise OSError("timeout waiting for response")

        # read data
        mv = self.dummybuf_memoryview
        if len(buf) != len(mv):
            mv = mv[: len(buf)]
        self.spi.write_readinto(mv, buf)

        # read checksum
        self.spi.write(b"\xff")
        self.spi.write(b"\xff")

        self.cs(1)
        self.spi.write(b"\xff")

    def write(self, token, buf):
        self.cs(0)

        # send: start of block, data, checksum
        self.spi.read(1, token)
        self.spi.write(buf)
        self.spi.write(b"\xff")
        self.spi.write(b"\xff")

        # check the response
        if (self.spi.read(1, 0xFF)[0] & 0x1F) != 0x05:
            self.cs(1)
            self.spi.write(b"\xff")
            return

        # wait for write to finish
        while self.spi.read(1, 0xFF)[0] == 0:
            pass

        self.cs(1)
        self.spi.write(b"\xff")

    def write_token(self, token):
        self.cs(0)
        self.spi.read(1, token)
        self.spi.write(b"\xff")
        # wait for write to finish
        while self.spi.read(1, 0xFF)[0] == 0x00:
            pass

        self.cs(1)
        self.spi.write(b"\xff")

    def readblocks(self, block_num, buf):
        nblocks = len(buf) // 512
        assert nblocks and not len(buf) % 512, "Buffer length is invalid"
        if nblocks == 1:
            # CMD17: set read address for single block
            if self.cmd(17, block_num * self.cdv, 0, release=False) != 0:
                # release the card
                self.cs(1)
                raise OSError("5: block_num=%d cdv=%d len(buf)=%d" % (block_num, self.cdv, len(buf)))  # EIO
            # receive the data and release card
            self.readinto(buf)

        else:
            # CMD18: set read address for multiple blocks
            if self.cmd(18, block_num * self.cdv, 0, release=False) != 0:
                # release the card
                self.cs(1)
                raise OSError(5)  # EIO
            offset = 0
            mv = memoryview(buf)
            while nblocks:
                # receive the data and release card
                self.readinto(mv[offset : offset + 512])
                offset += 512
                nblocks -= 1
            if self.cmd(12, 0, 0xFF, skip1=True):
                raise OSError(5)  # EIO

    def writeblocks(self, block_num, buf):
        nblocks, err = divmod(len(buf), 512)
        assert nblocks and not err, "Buffer length is invalid"
        if nblocks == 1:
            # CMD24: set write address for single block
            if self.cmd(24, block_num * self.cdv, 0) != 0:
                raise OSError(5)  # EIO

            # send the data
            self.write(_TOKEN_DATA, buf)
        else:
            # CMD25: set write address for first block
            if self.cmd(25, block_num * self.cdv, 0) != 0:
                raise OSError(5)  # EIO
            # send the data
            offset = 0
            mv = memoryview(buf)
            while nblocks:
                self.write(_TOKEN_CMD25, mv[offset : offset + 512])
                offset += 512
                nblocks -= 1
            self.write_token(_TOKEN_STOP_TRAN)

    def ioctl(self, op, arg):
        if op == 4:  # get number of blocks
            return self.sectors
