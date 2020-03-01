# Code by Simon Monk https://github.com/simonmonk/

from pirc522 import RFID
import RPi.GPIO as GPIO

class RFIDSausimat(RFID):
    def wait_for_tag(self, remove_callback = None):
        # enable IRQ on detect
        self.init()
        self.irq.clear()
        self.dev_write(0x04, 0x00)
        self.dev_write(0x02, 0xA0)
        # wait for it
        waiting = True
        while waiting:
            self.dev_write(0x09, 0x26)
            self.dev_write(0x01, 0x0C)
            self.dev_write(0x0D, 0x87)
            waiting = not self.irq.wait(0.1)
            if waiting and remove_callback:
                remove_callback()
                remove_callback = None
        self.irq.clear()
        self.init()


class MFRC522Sausimat:
    READER = None

    KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    BLOCK_ADDRS = [8, 9, 10]

    def __init__(self):
        self.READER = RFIDSausimat()
        self.UTIL = self.READER.util()

    def read(self):
        id, text = self.read_no_block()
        while not id:
            id, text = self.read_no_block()
        return id, text

    def read_id(self):
        id = self.read_id_no_block()
        while not id:
            id = self.read_id_no_block()
        return id

    def read_id_no_block(self):
        (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return None
        (status, uid) = self.READER.MFRC522_Anticoll()
        if status != self.READER.MI_OK:
            return None
        return self.uid_to_num(uid)

    def read_no_block(self, remove_callback = None):
        # Wait for tag
        self.READER.wait_for_tag(remove_callback = remove_callback)

        # Request tag
        (error, data) = self.READER.request()

        if not error:
            (error, uid) = self.READER.anticoll()
            if error:
                return None, None
            id = self.uid_to_num(uid)
            self.UTIL.set_tag(uid)
            self.UTIL.auth(self.READER.auth_a, self.KEY)
            error = self.UTIL.do_auth(11)
            if error:
                self.UTIL.deauth()
                return None, None

            data = []
            text_read = ''
            if not error:
                for block_num in self.BLOCK_ADDRS:
                    error, block = self.READER.read(block_num)
                    if block:
                        data += block
                if data:
                    text_read = ''.join(chr(i) for i in data)
            self.UTIL.deauth()
            return id, text_read
        else:
            return None, None

    def write(self, text):
        id, text_in = self.write_no_block(text)
        while not id:
            id, text_in = self.write_no_block(text)
        return id, text_in

    def write_no_block(self, text):
        (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return None, None
        (status, uid) = self.READER.MFRC522_Anticoll()
        if status != self.READER.MI_OK:
            return None, None
        id = self.uid_to_num(uid)
        self.READER.MFRC522_SelectTag(uid)
        status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, 11, self.KEY, uid)
        self.READER.MFRC522_Read(11)
        if status == self.READER.MI_OK:
            data = bytearray()
            data.extend(bytearray(text.ljust(len(self.BLOCK_ADDRS) * 16).encode('ascii')))
            i = 0
            for block_num in self.BLOCK_ADDRS:
                self.READER.MFRC522_Write(block_num, data[(i * 16):(i + 1) * 16])
                i += 1
        self.READER.MFRC522_StopCrypto1()
        return id, text[0:(len(self.BLOCK_ADDRS) * 16)]

    def uid_to_num(self, uid):
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n
