import logging
import time
import os


datetime = time.strftime("%Y%m%d-%H%M%S")
filename = f"logs/urban_{datetime}.log"
os.makedirs(os.path.dirname(filename), exist_ok=True)

logging.basicConfig(filename=filename,
            filemode='a',
            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            datefmt='%H:%M:%S',
            level=logging.DEBUG)

logger = logging.getLogger('bumblebee_pollination_abm')