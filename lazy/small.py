import logging
import time

LOG = logging.getLogger()
LOG.setLevel("DEBUG")

LOG.info("Sleeping!")
time.sleep(1)
LOG.info("Done sleeping!")

x = "Hello from small!"
