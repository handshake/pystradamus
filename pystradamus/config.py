import ConfigParser
import logging

log = logging.getLogger(__name__)

CONFIG_FILE_PATHS = ['.pystradamus.cfg', '~/pystradamus.cfg',
        '/etc/pystradamus.cfg']

def locate_and_parse(override_file):
    """Tries to open several paths as the main configuration file. If
    override_file is passed, it uses it exclusively. If None, then we
    go down the CONFIG_FILE_PATHS list in order til we find a valid config.

    If a configuration is loaded, return the ConfigParser object after parsing
    it. If no config can be located by above methods, return None
    """
    cfg = ConfigParser.ConfigParser()
    if override_file:
        try:
            cfg.readfp(override_file)
        except ConfigParser.Error as e:
            log.error("could not parse %s: %s", override_file.name, e.message)
            return None
    else:
        # see if we can find a config in known paths
        log.debug("searching for config at %s", CONFIG_FILE_PATHS)
        found = cfg.read(CONFIG_FILE_PATHS)
        log.debug("using config found at %s", found)
        if not found:
            return None
    return cfg

def main(args):
    """Prints out the sample config file so you can pipe it to a known location
    """
    from pkg_resources import resource_string
    print resource_string(__name__, 'etc/sample.cfg')
