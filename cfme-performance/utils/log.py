from py.path import local
from utils.conf import cfme_performance
from utils.path import get_rel_path, log_path
import logging
import os

# Additional Verbose Debug level
VDEBUG_LEVEL = 9


class _RelpathFilter(logging.Filter):
    """Adds the relpath attr to records

    Not actually a filter, this was the least ridiculous way to add custom dynamic
    record attributes and reduce it all down to the ``source`` record attr.

    looks for 'source_file' and 'source_lineno' on the log record, falls back to builtin
    record attributes if they aren't found.

    """
    def filter(self, record):
        try:
            relpath = get_rel_path(record.source_file)
            lineno = record.source_lineno
        except AttributeError:
            relpath = get_rel_path(record.pathname)
            lineno = record.lineno
        if lineno:
            record.source = "{}:{}".format(relpath, lineno)
        else:
            record.source = relpath

        return True


def vdebug(self, message, *args, **kws):
    self._log(VDEBUG_LEVEL, message, args, **kws)
logging.Logger.vdebug = vdebug

logging.addLevelName(VDEBUG_LEVEL, "VDEBUG")

logger = logging.getLogger('cfme-performance')
logger.setLevel(cfme_performance['logging']['level'])

formatter = logging.Formatter(
    '%(asctime)s : %(threadName)-11s : %(levelname)7s : %(message)s (%(source)s)')

# Main Log File
filehandler = logging.FileHandler(log_path.join('cfme-performance.log').strpath, 'a')
filehandler.setLevel(cfme_performance['logging']['level'])
filehandler.setFormatter(formatter)
logger.addFilter(_RelpathFilter())
logger.addHandler(filehandler)
