from data_handling.RoomAnalysis import RoomAnalysis
from threading import Lock
from color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)
from queue import Queue as _Queue

class DataHandler:
    def __init__(self, queue: _Queue, cv, config):
        # configurations
        self.queue = queue
        self.cv = cv

        self.config = config
        self.numRoom = config["numRoom"]
        self.roomsConf = config["room"]

        self.lock = Lock()
        self.rooms = dict()
    
    def put(self, topic, payload):
        #DEBUG
        logging.info(f'Receiving data from MQTT Topic: ["{color.bg_green(topic)}"]')
        logging.info(f'Data: {payload}')

        roomId, espId = topic.split("/")[1:3]
        if espId not in self.config["room"]["1"]["EspCoor"]:
            if espId == 'lib_esp32_\x0e':
                espId = 'lib_esp32_3'   # [BUG] Seem like it is cause by "lib_esp32_3"
            else:
                logging.error(f'[{espId = }], but expect: {self.config["room"]["1"]["EspCoor"]}')
                raise NameError(f'{espId = }')
        # topic ETS\%room\%esp:
        if roomId not in self.rooms:
            self.rooms[roomId] = RoomAnalysis(roomId, self.queue, self.cv, self.config)
        allRows = payload.split('\n')
        allRowsFiltered = list(filter(lambda x: x != "", allRows))
        header = allRowsFiltered[0]
        self.rooms[roomId].putData(espId, header, allRowsFiltered[1:])
