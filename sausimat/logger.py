import logging
from pathlib import Path


def create_logger(name: str, logfile_path: str, log_level: str):
    level = logging.getLevelName(log_level)
    do_logfile = True
    if not Path(logfile_path).parent.exists():
        do_logfile = False

    logging.basicConfig(level=logging.NOTSET)
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if do_logfile:
        fh = logging.FileHandler(logfile_path)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger