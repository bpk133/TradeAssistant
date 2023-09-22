import logging
from logging.handlers import SysLogHandler


def initiate_basic_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        filename="tradier_api.log")


def get_online_logger(name: str = 'default_logger', level=None):
    if level is None:
        level = logging.DEBUG
    papertrail_host = "logs6.papertrailapp.com"
    papertrail_port = 24237
    papertrail_handler = SysLogHandler(address=(papertrail_host, papertrail_port))
    logging.basicConfig(level=level,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[papertrail_handler])
    logger = logging.getLogger(name)
    # logger.setLevel(logging.DEBUG)
    # logger.addHandler(papertrail_handler)
    logger.info(f"logger initialized")
    return logger







