# from ..color import TTTT
# from color import setup
from color_log import color


def test():
  logging = color.setup(name='Sniffer', level=color.DEBUG)
  logging.debug("vleronovekrnerv")
  logging.info("vleronovekrnerv")
  logging.warning("vleronovekrnerv")
  logging.error("vleronovekrnerv")
  logging.critical("vleronovekrnerv")