import ConfigParser
import logging
import logging.handlers


class Config(ConfigParser.SafeConfigParser):
    """Wrapper of SafeConfigParser include some handy function
    """

    def __init__(self, path):
        ConfigParser.SafeConfigParser.__init__(self)
        if not self.read(path):
            raise IOError('cannot read configuration file: ' + path)

    def get(self, section, name, raw=None, var=None, default=None):
        try:
            val = ConfigParser.SafeConfigParser.get(self, section, name)
        except:
            val = default
        return val

    def get_bool(self, section, name, default=False):
        if self.has_option(section, name):
            value = self.get(section, name)
            if value.lower() == 'true':
                value = True
            else:
                value = False
        else:
            value = default
        return value

    def set_bool(self, section, name, value):
        if value:
            self.set(section, name, 'true')
        else:
            self.set(section, name, 'false')

    def get_int(self, section, name, default=0):
        try:
            value = self.getint(section, name)
        except:
            value = int(default)
        return value

    def get_float(self, section, name, default=0.0):
        try:
            val = self.getfloat(section, name)
        except:
            val = float(default)
        return val


cfg = Config('etc/config.ini')

log = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(level=cfg.get('Logging', 'log_level'))
    handler = logging.handlers.WatchedFileHandler(
        cfg.get('Logging', 'log_file'), mode='a')
    formatter = logging.Formatter(cfg.get('Logging', 'log_format'))
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)
    log.info("Logging enabled!")