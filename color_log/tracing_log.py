import time

class Tracing:
  def __init__(self) -> None:
    pass
  last_upload_tid: int = 0
  '''Trace the latest push ITD'''
  def now(self):
    '''return current time in seconds. (Unix timestamp)'''
    return int(time.time())
    


if __name__ == '__main__':
  ss = Tracing()
  
  print(ss.now())