import datetime
import time
import random
from wisepaasdatahubedgesdk.EdgeAgent import EdgeAgent
import wisepaasdatahubedgesdk.Common.Constants as constant
from wisepaasdatahubedgesdk.Model.Edge import (EdgeAgentOptions, MQTTOptions,
                                               DCCSOptions, EdgeData, EdgeTag,
                                               EdgeConfig, NodeConfig, DeviceConfig,
                                               )
from wise_paas.agent import (prepare_data,
                              create_tag,
                              create_device,
                              create_device_upload,
                              )
from color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)
from wise_paas import agent

# Constructor (EdgeAgentOptions options) 建立一個 EdgeAgent 物件.
options = EdgeAgentOptions(
  nodeId = '33431857-a315-4985-bb76-c96a2fcd3071',        
  # type = constant.EdgeType['Device'],                     # 節點類型 (Gateway, Device), 預設是 Gateway
  # deviceId = 'esp32_down',                                # 若 type 為 Device, 則必填
  # deviceId = 'Device1',                                # 若 type 為 Device, 則必填
  heartbeat = 60,                                         # 預設是 60 seconds
  dataRecover = True,                                     # 是否需要斷點續傳, 預設為 true
  connectType = constant.ConnectType['DCCS'],             # 連線類型 (DCCS, MQTT), 預設是 DCCS
                                                          # 若連線類型是 DCCS, DCCSOptions 為必填
  DCCS = DCCSOptions(
    apiUrl = 'https://api-dccs-ensaas.wise-paas.iotcenter.nycu.edu.tw/', # DCCS API Url
    credentialKey = '31f66480e439c63717968d15eb40a6nb'    # Creadential key
  )
)

edgeAgent = agent.setup(options)

config = EdgeConfig()
config.node = NodeConfig(nodeType=constant.EdgeType['Gateway'])

mqtt_temperature_1 = create_tag(name='mqtt_temperature_1',
                            description='窗邊 temperature',
                            readOnly=True,
                            arraySize=0,
                            spanHigh=36,
                            spanLow=20,
                            engineerUnit='°C',
                            integerDisplayFormat=2,
                            fractionDisplayFormat=1
                            )
mqtt_temperature_2 = create_tag(name='mqtt_temperature_2',
                            description='書架區 temperature',
                            readOnly=True,
                            arraySize=0,
                            spanHigh=36,
                            spanLow=20,
                            engineerUnit='°C',
                            integerDisplayFormat=2,
                            fractionDisplayFormat=1
                            )
mqtt_humidity_1 = create_tag(name='mqtt_humidity_1',
                            description='窗邊 humidity',
                            readOnly=True,
                            arraySize=0,
                            spanHigh=80,
                            spanLow=30,
                            engineerUnit='%',
                            integerDisplayFormat=2,
                            fractionDisplayFormat=0
                            )
mqtt_humidity_2 = create_tag(name='mqtt_humidity_2',
                            description='書架區 humidity',
                            readOnly=True,
                            arraySize=0,
                            spanHigh=80,
                            spanLow=30,
                            engineerUnit='%',
                            integerDisplayFormat=2,
                            fractionDisplayFormat=0
                            )
create_device(config=config,
              deviceId='dht11',
              description='Monitor the temperature and humidity.',
              deviceType='sensor'
              )

tag_list = [mqtt_temperature_1, mqtt_temperature_2,
            mqtt_humidity_1, mqtt_humidity_2
            ]

for _tag in tag_list:
  config.node.deviceList[0].analogTagList.append(_tag)

agent.config_upload(edgeAgent, config)

DELTA_T: int = 6
'''time shift between 2 sensors'''
LOOP_T: int = 60
'''time gap for looping sensors'''
DELTA_T *= .005
LOOP_T *= .005

# _start_minutes = 60*24*5
_start_minutes = 1

for jj in range(20000):
  _start_minutes -= 1
  if _start_minutes > 0:
    dummy_timestamp = datetime.datetime.now() - datetime.timedelta(minutes=_start_minutes)
  else:
    dummy_timestamp = datetime.datetime.now()
    DELTA_T = 6
    LOOP_T = 60

  if dummy_timestamp.hour > 22 or dummy_timestamp.hour < 9:
    delta_t = -random.uniform(0.1, 2.3)
    delta_h = random.uniform(1.7, 3.3)
  else:
    delta_t = 0
    delta_h = 0

# temperature-1
  edgeData = EdgeData()
  _measure_temperature_1 = round(random.uniform(24, 27)+delta_t+random.gauss(0.1, 0.7), 1)
  prepare_data(
    edgeData=edgeData,
    deviceId='dht11',
    tagName='mqtt_temperature_1',
    value=_measure_temperature_1,
    timestamp=dummy_timestamp
  )
  if not edgeAgent.sendData(data=edgeData):
    logging.error(f'Unable to send temperature data')
# humidity-1
  edgeData = EdgeData()
  _measure_humidity_1 = int(random.uniform(30, 50)+delta_h+random.gauss(0.3, 1.3))
  prepare_data(
    edgeData=edgeData,
    deviceId='dht11',
    tagName='mqtt_humidity_1',
    value=_measure_humidity_1,
    timestamp=dummy_timestamp
  )
  if not edgeAgent.sendData(data=edgeData):
    logging.error(f'Unable to send humidity data')
    
  time.sleep(DELTA_T)
  
# temperature-2
  edgeData = EdgeData()
  _measure_temperature_2 = round(random.uniform(24, 27)+delta_t+random.gauss(0.1, 0.7), 1)
  prepare_data(
    edgeData=edgeData,
    deviceId='dht11',
    tagName='mqtt_temperature_2',
    value=_measure_temperature_2,
    timestamp=dummy_timestamp
  )
  if not edgeAgent.sendData(data=edgeData):
    logging.error(f'Unable to send temperature data')
# humidity-2
  edgeData = EdgeData()
  _measure_humidity_2 = int(random.uniform(30, 50)+delta_h+random.gauss(0.3, 1.3))
  prepare_data(
    edgeData=edgeData,
    deviceId='dht11',
    tagName='mqtt_humidity_2',
    value=_measure_humidity_2,
    timestamp=dummy_timestamp
  )
  if not edgeAgent.sendData(data=edgeData):
    logging.error(f'Unable to send humidity data')

  
  logging.info(
    f'[{jj}] [{dummy_timestamp}]'
    f't1={_measure_temperature_1}°C, '
    f'h1={_measure_humidity_1}% | '
    f't2={_measure_temperature_2}°C, '
    f'h2={_measure_humidity_2}%'
    )
  time.sleep(LOOP_T - DELTA_T)




edgeAgent.disconnect()


# if '_main_' == _name_:
#   demo_create_deviceNtag(edgeAgent)

#   for i in range(10):
#     edgeData = gen_data()
#     result = edgeAgent.sendData(data=edgeData)
#     logging.debug(f'Send Data: {result=}')
#     time.sleep(1)
#     logging.info(f'[{edgeData.timestamp}] after sleep ==> data sent: {result}')


#   # while 1:
#   #   pass
#   edgeAgent.disconnect()import datetime
import time
import random
from wisepaasdatahubedgesdk.EdgeAgent import EdgeAgent
import wisepaasdatahubedgesdk.Common.Constants as constant
from wisepaasdatahubedgesdk.Model.Edge import (EdgeAgentOptions, MQTTOptions,
                                               DCCSOptions, EdgeData, EdgeTag,
                                               EdgeConfig, NodeConfig, DeviceConfig,
                                               )
from wise_paas.agent import (prepare_data,
                              create_tag,
                              create_device,
                              create_device_upload,
                              )
from color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)
from wise_paas import agent

# Constructor (EdgeAgentOptions options) 建立一個 EdgeAgent 物件.
options = EdgeAgentOptions(
  nodeId = '33431857-a315-4985-bb76-c96a2fcd3071',        
  # type = constant.EdgeType['Device'],                     # 節點類型 (Gateway, Device), 預設是 Gateway
  # deviceId = 'esp32_down',                                # 若 type 為 Device, 則必填
  # deviceId = 'Device1',                                # 若 type 為 Device, 則必填
  heartbeat = 60,                                         # 預設是 60 seconds
  dataRecover = True,                                     # 是否需要斷點續傳, 預設為 true
  connectType = constant.ConnectType['DCCS'],             # 連線類型 (DCCS, MQTT), 預設是 DCCS
                                                          # 若連線類型是 DCCS, DCCSOptions 為必填
  DCCS = DCCSOptions(
    apiUrl = 'https://api-dccs-ensaas.wise-paas.iotcenter.nycu.edu.tw/', # DCCS API Url
    credentialKey = '31f66480e439c63717968d15eb40a6nb'    # Creadential key
  )
)

edgeAgent = agent.setup(options)

config = EdgeConfig()
config.node = NodeConfig(nodeType=constant.EdgeType['Gateway'])

mqtt_temperature_1 = create_tag(name='mqtt_temperature_1',
                            description='窗邊 temperature',
                            readOnly=True,
                            arraySize=0,
                            spanHigh=36,
                            spanLow=20,
                            engineerUnit='°C',
                            integerDisplayFormat=2,
                            fractionDisplayFormat=1
                            )
mqtt_temperature_2 = create_tag(name='mqtt_temperature_2',
                            description='書架區 temperature',
                            readOnly=True,
                            arraySize=0,
                            spanHigh=36,
                            spanLow=20,
                            engineerUnit='°C',
                            integerDisplayFormat=2,
                            fractionDisplayFormat=1
                            )
mqtt_humidity_1 = create_tag(name='mqtt_humidity_1',
                            description='窗邊 humidity',
                            readOnly=True,
                            arraySize=0,
                            spanHigh=80,
                            spanLow=30,
                            engineerUnit='%',
                            integerDisplayFormat=2,
                            fractionDisplayFormat=0
                            )
mqtt_humidity_2 = create_tag(name='mqtt_humidity_2',
                            description='書架區 humidity',
                            readOnly=True,
                            arraySize=0,
                            spanHigh=80,
                            spanLow=30,
                            engineerUnit='%',
                            integerDisplayFormat=2,
                            fractionDisplayFormat=0
                            )
create_device(config=config,
              deviceId='dht11',
              description='Monitor the temperature and humidity.',
              deviceType='sensor'
              )

tag_list = [mqtt_temperature_1, mqtt_temperature_2,
            mqtt_humidity_1, mqtt_humidity_2
            ]

for _tag in tag_list:
  config.node.deviceList[0].analogTagList.append(_tag)

agent.config_upload(edgeAgent, config)

DELTA_T: int = 6
'''time shift between 2 sensors'''
LOOP_T: int = 60
'''time gap for looping sensors'''
DELTA_T *= .005
LOOP_T *= .005

# _start_minutes = 60*24*5
_start_minutes = 1

for jj in range(20000):
  _start_minutes -= 1
  if _start_minutes > 0:
    dummy_timestamp = datetime.datetime.now() - datetime.timedelta(minutes=_start_minutes)
  else:
    dummy_timestamp = datetime.datetime.now()
    DELTA_T = 6
    LOOP_T = 60

  if dummy_timestamp.hour > 22 or dummy_timestamp.hour < 9:
    delta_t = -random.uniform(0.1, 2.3)
    delta_h = random.uniform(1.7, 3.3)
  else:
    delta_t = 0
    delta_h = 0

# temperature-1
  edgeData = EdgeData()
  _measure_temperature_1 = round(random.uniform(24, 27)+delta_t+random.gauss(0.1, 0.7), 1)
  prepare_data(
    edgeData=edgeData,
    deviceId='dht11',
    tagName='mqtt_temperature_1',
    value=_measure_temperature_1,
    timestamp=dummy_timestamp
  )
  if not edgeAgent.sendData(data=edgeData):
    logging.error(f'Unable to send temperature data')
# humidity-1
  edgeData = EdgeData()
  _measure_humidity_1 = int(random.uniform(30, 50)+delta_h+random.gauss(0.3, 1.3))
  prepare_data(
    edgeData=edgeData,
    deviceId='dht11',
    tagName='mqtt_humidity_1',
    value=_measure_humidity_1,
    timestamp=dummy_timestamp
  )
  if not edgeAgent.sendData(data=edgeData):
    logging.error(f'Unable to send humidity data')
    
  time.sleep(DELTA_T)
  
# temperature-2
  edgeData = EdgeData()
  _measure_temperature_2 = round(random.uniform(24, 27)+delta_t+random.gauss(0.1, 0.7), 1)
  prepare_data(
    edgeData=edgeData,
    deviceId='dht11',
    tagName='mqtt_temperature_2',
    value=_measure_temperature_2,
    timestamp=dummy_timestamp
  )
  if not edgeAgent.sendData(data=edgeData):
    logging.error(f'Unable to send temperature data')
# humidity-2
  edgeData = EdgeData()
  _measure_humidity_2 = int(random.uniform(30, 50)+delta_h+random.gauss(0.3, 1.3))
  prepare_data(
    edgeData=edgeData,
    deviceId='dht11',
    tagName='mqtt_humidity_2',
    value=_measure_humidity_2,
    timestamp=dummy_timestamp
  )
  if not edgeAgent.sendData(data=edgeData):
    logging.error(f'Unable to send humidity data')

  
  logging.info(
    f'[{jj}] [{dummy_timestamp}]'
    f't1={_measure_temperature_1}°C, '
    f'h1={_measure_humidity_1}% | '
    f't2={_measure_temperature_2}°C, '
    f'h2={_measure_humidity_2}%'
    )
  time.sleep(LOOP_T - DELTA_T)




edgeAgent.disconnect()


# if '_main_' == _name_:
#   demo_create_deviceNtag(edgeAgent)

#   for i in range(10):
#     edgeData = gen_data()
#     result = edgeAgent.sendData(data=edgeData)
#     logging.debug(f'Send Data: {result=}')
#     time.sleep(1)
#     logging.info(f'[{edgeData.timestamp}] after sleep ==> data sent: {result}')


#   # while 1:
#   #   pass
#   edgeAgent.disconnect()