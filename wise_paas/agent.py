import datetime
import time
import random
from wisepaasdatahubedgesdk.EdgeAgent import EdgeAgent
import wisepaasdatahubedgesdk.Common.Constants as constant
# from wisepaasdatahubedgesdk.Common.Utils import RepeatedTimer
from wisepaasdatahubedgesdk.Model.Edge import (EdgeAgentOptions, MQTTOptions,
                                               DCCSOptions, EdgeData, EdgeTag,
                                               EdgeStatus, EdgeDeviceStatus,
                                               EdgeConfig, NodeConfig, DeviceConfig,
                                               AnalogTagConfig, DiscreteTagConfig, TextTagConfig
                                               )
from color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)

'''
# Event
EdgeAgent 有以下三種事件可供訂閱
  - Connected: 當 EdgeAgent 與 IoTHub 連線成功時觸發
  - Disconnected: 當 EdgeAgent 與 IoTHub 斷線時觸發
  - MessageReceived: 當 EdgeAgent 接收到 雲端指令時觸發. 訊息類型有以下幾種:
    1. WriteValue: 修改設備端測點值
    2. WriteConfig: 修改設備端 Config
    3. TimeSync: 回傳目前雲端伺服器時間, 供時間同步使用
    4. ConfigAck: 雲端處理完地端發送的 Config 同步後所回傳的訊息
'''
def edgeAgent_on_connected(agent, isConnected):
  logging.info('Connected!')
def edgeAgent_on_disconnected(agent, isDisconnected):
  logging.info('Disconnected')
def edgeAgent_on_message(agent, messageReceivedEventArgs):
  # messageReceivedEventArgs format: Model.Event.MessageReceivedEventArgs
  type = messageReceivedEventArgs.type
  message = messageReceivedEventArgs.message
  if type == constant.MessageType['WriteValue']:
    # message format: Model.Edge.WriteValueCommand
    for device in message.deviceList:
      logging.info('deviceId: {0}'.format(device.id))
      for tag in device.tagList:
        logging.info('tagName: {0}, Value: {1}'.format(tag.name, str(tag.value)))
  elif type == constant.MessageType['WriteConfig']:
    logging.info('WriteConfig')
  elif type == constant.MessageType['TimeSync']:
    # message format: Model.Edge.TimeSyncCommand
    logging.info(str(message.UTCTime))
  elif type == constant.MessageType['ConfigAck']:
    # message format: Model.Edge.ConfigAck
    if not message.result:
      logging.warning(f'Upload Config Result: {message.result}')
    else:
      logging.info(f'Upload Config Result: {message.result}')


def prepare_data(
  edgeData: EdgeData,
  deviceId: str,
  tagName: str,
  value,
  timestamp=None,
):
  '''Prepare data in advance. Shoud use with `sendData(...)`.'''
  tag = EdgeTag(deviceId, tagName, value)
  edgeData.tagList.append(tag)
  if timestamp is None:
    edgeData.timestamp = datetime.datetime.now()
  else:
    edgeData.timestamp = timestamp
  # logging.error(datetime.datetime.now())

def create_tag(
  name: str='ATag',
  description: str='AnalogTag',
  readOnly: bool=True,
  arraySize: int=0,
  spanHigh: int=100,
  spanLow: int=0,
  engineerUnit: str=None,
  integerDisplayFormat: int=3,
  fractionDisplayFormat: int=4
):
  '''Analog Tag config setting'''
  analogTag = AnalogTagConfig(name, description, readOnly,
                              arraySize, spanHigh, spanLow,
                              engineerUnit, integerDisplayFormat,
                              fractionDisplayFormat)
  return analogTag

def create_device(
  config: EdgeConfig,
  deviceId: str,
  deviceType: str,
  description:str,
  analogTag: AnalogTagConfig=None,
):
  '''Node config setting'''
  config.node = NodeConfig(nodeType=constant.EdgeType['Gateway'])

  deviceConfig = DeviceConfig(
    id=deviceId,
    name=deviceId,
    deviceType=deviceType,
    description=description
  )
  '''Device config setting'''
  config.node.deviceList.append(deviceConfig)
  if analogTag is not None:
    config.node.deviceList[0].analogTagList.append(analogTag)

def create_device_upload(
  edgeAgent: EdgeAgent,
  deviceId: str,
  deviceType: str,
  description:str,
  analogTag: AnalogTagConfig=None,
):
  '''Lazy way to create a device and upload.'''
  config = EdgeConfig()
  config.node = NodeConfig(nodeType=constant.EdgeType['Gateway'])

  deviceConfig = DeviceConfig(
    id=deviceId,
    name=deviceId,
    deviceType=deviceType,
    description=description
  )
  '''Device config setting'''
  config.node.deviceList.append(deviceConfig)
  if analogTag is not None:
    config.node.deviceList[0].analogTagList.append(analogTag)
  result = edgeAgent.uploadConfig(constant.ActionType['Create'], edgeConfig=config)
  logging.debug(f'[{deviceType=}, {description=}, {deviceId=}] Upload Config: {result}')
  
  return result

def config_upload(
  edgeAgent: EdgeAgent,
  config: EdgeConfig,
):
  result = edgeAgent.uploadConfig(constant.ActionType['Create'], edgeConfig=config)
  logging.debug(f'Upload Config: {result}')

# --------- DEMO --------- #
def demo_create_deviceNtag(edgeAgent: EdgeAgent):
  for _j in range(1, 3):
    config = EdgeConfig()
    '''
    UploadConfig ( ActionType action, EdgeConfig edgeConfig )
    上傳 Node/Device/Tag Config, 有三種同步類型(Create/Update/Delete)
    - set node config
    - set device config
    - set tag config
    '''
    # Node config setting
    nodeConfig = NodeConfig(nodeType=constant.EdgeType['Gateway'])
    config.node = nodeConfig
    
    create_device(config=config,
                  deviceId=f'Device{_j}',
                  description='Device Type',
                  deviceType='Description',
                  )

    for i in range(1, 5):
      analogTag = AnalogTagConfig(
        name = f'ATag{i}',
        description = 'AnalogTag',
        readOnly = True,
        arraySize = 0,
        spanHigh = 10,
        spanLow = 0,
        engineerUnit = 'cm',
        integerDisplayFormat = 2,
        fractionDisplayFormat = 4
      )

      config.node.deviceList[0].analogTagList.append(analogTag)

    for i in range(1, 5):
      discreteTag = DiscreteTagConfig(
        name = f'DTag{i}',
        description = 'DiscreteTag',
        readOnly = False,
        arraySize = 0,
        state0 = '1',
        state1 = '0',
        state2 = None,
        state3 = None,
        state4 = None,
        state5 = None,
        state6 = None,
        state7 = None
      )
      '''Discrete Tag config setting'''
      config.node.deviceList[0].discreteTagList.append(discreteTag)

    for i in range(1, 5):
      textTag = TextTagConfig(
        name = f'TTag{i}',
        description = 'TextTag',
        readOnly = True,
        arraySize = 0
      )
      '''Text tag config setting'''
      config.node.deviceList[0].textTagList.append(textTag)

    config_upload(edgeAgent, config)


def gen_data():
  '''Create random content.'''
  edgeData = EdgeData()
  for i in range(1, 3):
    for j in range(1, 5):
      prepare_data(
        edgeData=edgeData,
        deviceId=f'Device{i}',
        tagName=f'ATag{j}',
        value=random.uniform(0, 100),
      )
    for j in range(1, 5):
      prepare_data(
        edgeData=edgeData,
        deviceId=f'Device{i}',
        tagName=f'DTag{j}',
        value=random.randint(0, 99) % 2,
      )
    for j in range(1, 5):
      prepare_data(
        edgeData=edgeData,
        deviceId=f'Device{i}',
        tagName=f'TTag{j}',
        value=f'TEST {j}',
      )
  return edgeData


def setup(options: EdgeAgentOptions):
  edgeAgent = EdgeAgent(options=options)
  edgeAgent.on_connected = edgeAgent_on_connected
  edgeAgent.on_disconnected = edgeAgent_on_disconnected
  edgeAgent.on_message = edgeAgent_on_message
  logging.info('Connecting to Agent...')
  edgeAgent.connect()
  while not edgeAgent.isConnected():
    time.sleep(0.01)  # Waiting for connection to be established
  return edgeAgent


