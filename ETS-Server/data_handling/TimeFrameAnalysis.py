import pandas as pd
from color_log import color
logging = color.setup(name=__name__, level=color.INFO)

from utility.utility import isLast


class TimeFrameAnalysis:
    def __init__(self, tid, numEsp, roomid):
        # the tid start of the time analysis
        self.tid = tid
        # numbers of esp in the room
        self.numEsp = numEsp
        # id of the room
        self.roomid = roomid
        # numbers of esp that has completed their analysis
        self.nCompleted = 0
        # Data
        self.entries = list()

    def putRows(self, espId, header, rows, bypass: bool=False):
        '''
        Check if the received package from esp32 is equals to expected value.
        * If `bypass` is `True`, it will return `True` without meeting the condition.
        
        The entry is split into a list composed by measures and values
        
        `ESPID(added there) | MAC | SSID | TIMESTAMP | HASH | RSSI | SN | HTCI`
        
        The SSID can contain space, so the lenght of the entry should be checked, and if it
        exceed the normal lenght, the ssid should be riconstructed and be put in one element
        of the vector entry_reformed
        '''
        _return: bool = False
        for row in rows:
            entry = row.split(" ")
            len_ent = len(entry)
            if len_ent >= 8:
                entry_reformed = list()
                entry_reformed.append(espId)
                entry_reformed = entry_reformed + entry[:1]
                entry_reformed.append(' '.join(entry[1: len_ent - 5]))
                entry_reformed = entry_reformed + entry[len_ent - 5:]
                self.entries.append(entry_reformed)
            elif len_ent == 7:
                entry.insert(0, espId)
                self.entries.append(entry)
            else:
                logging.warning(f'Invalid entry: {entry} {len(entry[0])=} \nCleaning...')
                entry = []
        # If it's the last of the minute timestamp, i increase the counter of completed frames
        # If all the packets of all ESP32 were sent, i put return True in order to put them into the queue
        if isLast(header):
            logging.info(f"Last packet sent from [{espId=}]. (Timestamp={header.split(' ')[1]})")
            self.nCompleted = self.nCompleted + 1
            logging.info(color.bg_yellow(f"Actual number of bunch of data: {self.nCompleted}, Waiting: {self.numEsp}"))
            if self.nCompleted == self.numEsp:
                _return = True
        return True if bypass else _return

    def getDataFrame(self):
        return pd.DataFrame(self.entries, columns=['ESPID','MAC','SSID','TIMESTAMP','HASH','RSSI','SN','HTCI'])

