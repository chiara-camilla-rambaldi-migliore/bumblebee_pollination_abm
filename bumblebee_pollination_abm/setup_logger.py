import logging
import time


datetime = time.strftime("%Y%m%d-%H%M%S")
logging.basicConfig(filename=f"logs/urban_{datetime}.log",
            filemode='a',
            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            datefmt='%H:%M:%S',
            level=logging.DEBUG)

logger = logging.getLogger('bumblebee_pollination_abm')