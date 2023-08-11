from queue import Queue
from threading import Lock, Condition, Thread
from time import sleep
from color_log import color

from analysis.Analyzer import Analyzer
from mqtt import MQTTDummyPublisher
from mqtt import MQTTListener


def run_mqtt(mqttclient):
    mqttclient.start()
    #mqttclient.loop()


def run_mqtt_dummy(mqttclient: MQTTDummyPublisher):
    mqttclient.start()
    mqttclient.dummy_pubblish("mqtt/sample_fakedata_1.csv")


class EtsServer:
    def __init__(self, config, dummy=False, db_persistence=False):

        # variables for multithreading
        self.q = Queue()
        self.cv = Condition()
        self.dummy = dummy
        self.log_level = color.DEBUG
        self._config = config
        self._persist = db_persistence

        # classes
        self.mqttl = MQTTListener(self.q, self.cv, config, log_level=self.log_level)
        self.analyzer = Analyzer(self.q, self.cv, config, db_persistence, log_level=self.log_level)
        if dummy:
            self.mqttfp = MQTTDummyPublisher(config)

        # threads
        self.thread_mqttl = Thread(target=run_mqtt, args=(self.mqttl,))
        if dummy:
            self.thread_mqttfp = Thread(target=run_mqtt_dummy, args=(self.mqttfp,))

    def start(self):
        self.analyzer.start()
        self.thread_mqttl.start()
        if self.dummy:
            sleep(1)
            self.thread_mqttfp.start()

    def stop(self):
        # we declare to stop everything
        self.analyzer.stop()
        self.mqttl.stop()
        if self.dummy:
            self.mqttfp.stop()

        # join threads
        if self.dummy:
            self.thread_mqttfp.join()
        self.thread_mqttl.join()
    
    def debug_off(self):        
        if self.log_level == color.DEBUG:
            self.analyzer.stop()
            self.mqttl.stop()
            self.thread_mqttl.join()
            
            self.log_level = color.INFO
            self.mqttl = MQTTListener(self.q, self.cv, self._config, log_level=self.log_level)
            self.analyzer = Analyzer(self.q, self.cv, self._config, self._persist, log_level=self.log_level)
            self.thread_mqttl = Thread(target=run_mqtt, args=(self.mqttl,))
            
            self.analyzer.start()
            self.thread_mqttl.start()
            print('DEBUG was turned off.')
        else:
            print('DEBUG is already off.')

    def debug_on(self):
        if self.log_level != color.DEBUG:
            self.analyzer.stop()
            self.mqttl.stop()
            self.thread_mqttl.join()

            self.log_level = color.DEBUG
            self.mqttl = MQTTListener(self.q, self.cv, self._config, log_level=self.log_level)
            self.analyzer = Analyzer(self.q, self.cv, self._config, self._persist, log_level=self.log_level)
            self.thread_mqttl = Thread(target=run_mqtt, args=(self.mqttl,))
            
            self.analyzer.start()
            self.thread_mqttl.start()
            print('DEBUG was turned on.')
        else:
            print('DEBUG is already on.')