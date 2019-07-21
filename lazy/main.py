import logging
import sys

from lazy import activate_lazy_imports

LOG = logging.getLogger()
LOG.setLevel("DEBUG")

activate_lazy_imports()

LOG.info("Importing module small")
import small
LOG.info("Module small 'imported'")

LOG.info(small.x)
LOG.info(small.__name__)

LOG.info("Done")
