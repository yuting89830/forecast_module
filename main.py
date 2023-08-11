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
from forecast import load_and_process_data, train_and_predict

# Constructor (EdgeAgentOptions options) 建立一個 EdgeAgent 物件.
options = EdgeAgentOptions(
  nodeId = '9946b1f7-59e9-4daa-8f1d-8d8dda60316f',        
  # type = constant.EdgeType['Device'],                     # 節點類型 (Gateway, Device), 預設是 Gateway
  # deviceId = 'esp32_down',                                # 若 type 為 Device, 則必填
  # deviceId = 'Device1',                                # 若 type 為 Device, 則必填
  heartbeat = 60,                                         # 預設是 60 seconds
  dataRecover = True,                                     # 是否需要斷點續傳, 預設為 true
  connectType = constant.ConnectType['DCCS'],             # 連線類型 (DCCS, MQTT), 預設是 DCCS
                                                          # 若連線類型是 DCCS, DCCSOptions 為必填
  DCCS = DCCSOptions(
    apiUrl = 'https://api-dccs-ensaas.wise-paas.iotcenter.nycu.edu.tw/', # DCCS API Url
    credentialKey = '8c6c294859cab1d92532a4ffa5952ata'    # Creadential key
  )
)

edgeAgent = agent.setup(options)

config = EdgeConfig()
config.node = NodeConfig(nodeType=constant.EdgeType['Gateway'])

result_AR = create_tag(name='result_AR',
                        description='...',
                        readOnly=True,
                        arraySize=0,
                        spanHigh=200,
                        spanLow=0,
                        engineerUnit='people',
                        integerDisplayFormat=3,
                        fractionDisplayFormat=0
                        )
result_LSTM = create_tag(name='result_LSTM',
                        description='...',
                        readOnly=True,
                        arraySize=0,
                        spanHigh=200,
                        spanLow=0,
                        engineerUnit='people',
                        integerDisplayFormat=3,
                        fractionDisplayFormat=0
                        )

create_device(config=config,
              deviceId='result',
              description='...',
              deviceType='forecast'
              )

tag_list = [result_AR, result_LSTM,
            ]
for _tag in tag_list:
  config.node.deviceList[0].analogTagList.append(_tag)

agent.config_upload(edgeAgent, config)
data_file_path = 'grafana_data_process.csv'
# Load and process data
series = load_and_process_data(data_file_path)
# Train and predict
predictions = train_and_predict(series)
# Output all predictions
for i, pred in enumerate(predictions):
    print(f'[{i}] predicted={int(pred)}')

# Train and predict
predictions = train_and_predict(series)

# Update dummy_result with predictions
dummy_result = []  # Initialize an empty list

# Loop to store each prediction in dummy_result
for pred in predictions:
    dummy_result.append(int(pred))

for _id, result in enumerate(dummy_result, start=1):
    delta_time = datetime.datetime.now() + datetime.timedelta(minutes=30*_id) # 每30分鐘更新
    edgeData = EdgeData()
    prepare_data(
        edgeData=edgeData,
        deviceId='result',
        tagName='result_AR',
        value=result,
        timestamp=delta_time,
    )
    if not edgeAgent.sendData(data=edgeData):
        logging.error(f'Unable to send forecasting data')
    logging.info(f'[{delta_time}] Predicted {result = }')
    time.sleep(.005)
    





edgeAgent.disconnect()
