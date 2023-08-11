from copy import deepcopy
from threading import Lock
from color_log import color, tracing_log
logging = color.setup(name=__name__, level=color.DEBUG)
from data_handling.TimeFrameAnalysis import TimeFrameAnalysis
from utility.utility import getTid
from queue import Queue as _Queue


class RoomAnalysis:
    def __init__(self, id, queue: _Queue, cv, config):
        self.config = config

        # Configuring multiThreading obj
        self.queue: _Queue = queue
        self.cv = cv
    
        self.roomId = id
        self.currTid = -1
        self.numEsp = config["room"][self.roomId]["numEsp"]
        self.currentAnalysisData = TimeFrameAnalysis(-1, 1, id)
        # tracing_log.Tracing.last_upload_tid = self.currTid
        self.tracing = tracing_log.Tracing()
        logging.debug(color.bg_purple(f'Start tracing! Current TID={self.tracing.now()}'))
        self.tracing.last_upload_tid = self.tracing.now()

        self.lock = Lock()

    
    def putData(self, espId, header, rows):
        '''This function will calibration the TID(Time ID) whenever the data received'''
        espTid = getTid(header)
        _bypass = False
        # DEBUG
        # print("Trying to take the lock for the room: ",self.roomId)
        logging.debug(color.bg_purple(f'Last push:  {self.tracing.last_upload_tid}'))
        if abs(self.tracing.now() - self.tracing.last_upload_tid) >= 60*2:    # Force push every 2 minutes!
            logging.debug(color.bg_purple(
                f'Unable to receive all packet for {self.tracing.now() - self.tracing.last_upload_tid} seconds. ') + \
                        color.bg_red('Force pushing to the queue!'))
            _bypass = True

        if espTid < self.currTid:
            logging.warning("Old packet, all the packets captured that are written into it will not be be analyzed")
        elif espTid == self.currTid:
            logging.debug(f"for [{espTid=}]: packets were sent, check if it is the last one")
            if self.currentAnalysisData.putRows(espId, header, rows, bypass=_bypass):
                logging.info(f"for [{espTid=}]: all the packets were sent, putting it into the queue")
                self.putDataQueue()
                logging.debug(f'{self.currentAnalysisData.getDataFrame() = }')
                self.currTid += self.config['Sniffing_time']
                self.tracing.last_upload_tid = self.currTid     # tracing last upload (to queue)
                with self.lock:
                    self.currentAnalysisData = TimeFrameAnalysis(self.currTid, self.numEsp, self.roomId)

        else:
            # The current Time id it's updated, because from now the analysis will be done refering to new Time id
            self.currTid = espTid
            # TODO analyze data with what i have?
            with self.lock:
                self.currentAnalysisData = TimeFrameAnalysis(self.currTid, self.numEsp, self.roomId)
            # if abs(self.tracing.now() - self.tracing.last_upload_tid) >= 60*2:    # Force push every 2 minutes!
            #     logging.debug(color.bg_purple(
            #         f'Unable to receive all packet for {self.tracing.now() - self.tracing.last_upload_tid} seconds. ') + \
            #                 color.bg_red('Force pushing to the queue!'))
            #     _bypass = True
            if self.currentAnalysisData.putRows(espId, header, rows, bypass=_bypass):
                self.putDataQueue()
                self.tracing.last_upload_tid = self.currTid     # tracing last upload (to queue)

    def putDataQueue(self):
        with self.cv:
            self.cv.wait(timeout=4)
            # logging.warning(f'{self.queue.qsize() = }')
            with self.lock:
                # print('*%'*60)
                self.queue.put(deepcopy(self.currentAnalysisData))
            logging.debug(f'{self.queue.qsize() = }')
            self.cv.notify_all()
