import logging

logging.basicConfig(filename=f"logs/test.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running Urban Planning")

logger = logging.getLogger(f"test")

logger.info("Test info")
logger.debug("Test debug")

pippo = logger

pippo.debug("Test debug 2")