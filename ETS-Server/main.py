import argparse
import yaml
import threading
from color_log import color
logging = color.setup(name='Sniffer', level=color.DEBUG)
from server.EtsServer import EtsServer
import sys
import subprocess


def main(config, persistence, dummy):
  # parameters initalization
  logging.warning(f"{persistence=}, {dummy=}")
  ets = EtsServer(config, dummy=dummy, db_persistence=persistence)
  ets.start()
  cli_history: list = ['debug off', 'debug off all', 'debug on', 'debug on all']
  _lock_cli: bool = True
  _lock_input: bool = True
  go: bool = True
  logging.info("Typing 'stop' to terminate the server.")
  while go:
    _input_str: str = ""
    
    if _lock_input:
      print('>>> ', end='', flush=True)
      while True:
        c = sys.stdin.read(1)
        if c == '\n':
          break
        else:
          _input_str += c

      cli_command = _input_str        # Bypass this to activate from 'hist'
      cli_history.append(cli_command) # Won't log to history if using 'hist'
    
    _lock_input = True

    if cli_command == "stop":
      go = False
    elif cli_command == "debug off all":
      _lock_cli = True
      logging.setLevel(color.INFO)
      logging.warning('Turn off all DEBUG msg')
    elif cli_command == "debug on all":
      _lock_cli = True
      logging.setLevel(color.DEBUG)
      logging.warning('Turn on all DEBUG msg')

    elif cli_command == "debug off":
      _lock_cli = True
      # logging.info('run "ets.debug_off()"')
      ets.debug_off()
    elif cli_command == "debug on":
      _lock_cli = True
      # logging.info('run "ets.debug_on()"')
      ets.debug_on()

    elif cli_command[:4] == "hist":
      _lock_cli = True
      cli_history.pop()
      _cli_commands = cli_command.split(' ')
      if len(_cli_commands) == 1:
        logging.info(f'{cli_history = }')
      elif len(_cli_commands) == 2:
        try:
          if len(cli_history) > int(_cli_commands[-1]):
            cli_command = cli_history[int(_cli_commands[-1])]
            _lock_input = False
          else:
            logging.error(f'Out of range. {cli_history = }')
        except:
          logging.error(f'Can\'t handle that. [{_cli_commands[1] = }]')

    elif len(cli_command)>1 and cli_command[0]=='!':
      _lock_cli = True
      if len(cli_command[1:])>1:
        try:
          _cli_commands = cli_command[1:].split(' ')
          process_1 = subprocess.run(_cli_commands)
          logging.info(f'{process_1 = }')
        except:
          cli_history.pop()
          logging.error("Not allowed.")

    elif len(cli_command)<1:
      _lock_cli = False
      cli_history.pop()
      pass

    else:
      _lock_cli = True
      cli_history.pop()
      logging.critical('FUNCTION NOT ALLOWED. Typing "stop" to terminate the server.')
      # logging.info("Typing 'stop' to terminate the server.")
    
    if _lock_cli and _lock_input:
      logging.debug(f"{'='*30} {cli_command} {'='*30}")

  logging.info('Goodbye!')
  ets.stop()


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='ETS Server')
  parser.add_argument('-c', '--config', default=None, type=str, 
                      help='config file path (default: configurations.yaml)')
  parser.add_argument('-p', '--persistence', default=True, action='store_true', 
                      help='use to avoid to clean existing database')
  parser.add_argument('-fp', '--dummy', action='store_true', 
                      help='Run the mqtt dummy publisher')

  args = parser.parse_args()
  config = {}
  if args.config:
    filename = args.config 
    # os.path.join(os.path.dirname(__file__), args.config)
  else:
    filename = 'configurations.yaml' 
    # os.path.join(os.path.dirname(__file__), 'configurations.yaml')
  try:
    with open(filename, 'r') as f:
      config = yaml.load(f, yaml.FullLoader)
  except Exception as e:
    logging.critical(e)
    exit(-1)
  main(config,
       True if args.persistence else False,
       True if args.dummy else False)
