#!/usr/bin/env python
# -*- coding:utf-8 -*-

import threading
import serial
import parser
import time


COMMAND_BYTES = {
    'auto_connect': '\xc2',
    'disconnect': '\xc1',
}

class DongleReader(threading.Thread):
    def __init__(self, parser, *args, **kwargs):
        self.parser = parser
        self.running = True
        super(DongleReader, self).__init__(*args, **kwargs)

    def run(self):
        while self.running:
            if not self.parser.sending_data:
                time.sleep(0.5)
            self.parser.update()

    def stop(self):
        self.running = False
        self._Thread__stop()


class Headset():
    def __init__(self, dongle_dev, global_id=None):
        if global_id:
            self.auto_connect = False
            self.global_id = global_id
        else:
            self.auto_connect = True
        self.dongle_dev = dongle_dev
        self.dongle_fs = serial.Serial(dongle_dev,  115200, timeout=0.001)
        self.parser = parser.VirtualParser(self.dongle_fs)
        # setup listening thread
        self.dongle_reader = DongleReader(self.parser)
        self.dongle_reader.daemon = True
        self.dongle_reader.start()

    def connect(self):
        if self.auto_connect:
            self.dongle_fs.write(COMMAND_BYTES['auto_connect'])
        else:
            #@TODO connect to specific headset  11.07 2013 (houqp)
            pass

    def disconnect(self):
        self.dongle_fs.write(COMMAND_BYTES['disconnect'])

    def destroy(self):
        self.dongle_reader.stop()
        self.dongle_fs.close()

    def get_state(self):
        return self.parser.dongle_state

    def get_current_attention(self):
        return self.parser.current_attention

    def get_current_meditation(self):
        return self.parser.current_meditation

    def get_rawdata(self):
        return self.parser.raw_values

    def get_waves_vector(self):
        return self.parser.current_vector


    def get(self, stuff):
        if stuff == 'rawdata':
            return self.get_rawdata()
        elif stuff == 'state':
            return self.get_state()
        elif stuff == 'waves_vector':
            return self.get_waves_vector()
        else:
            return None

