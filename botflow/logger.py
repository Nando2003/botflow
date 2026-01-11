import logging
from datetime import datetime as dt
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def configure_logger(
    name: str = 'big_views',
    log_dir: str | Path = './logs',
    level: int = logging.INFO,
    console: bool = True,
    rotating_file: bool = True,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

    if rotating_file:
        log_name = dt.now().strftime('%d-%m-%Y_%Hh-%Mm-%Ss')
        log_path = log_dir / f'{log_name}.log'

        file_handler = TimedRotatingFileHandler(
            filename=str(log_path),
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8',
        )
        file_handler.suffix = '%Y%m%d'
        file_handler.setLevel(level)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(fmt)
        logger.addHandler(console_handler)

    return logger
