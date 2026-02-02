from __future__ import annotations

import datetime
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Optional


def setup_logging(log_config: dict) -> logging.Logger:
    logger = logging.getLogger("yuyan")
    if logger.handlers:
        return logger
    level = log_config.get("LEVEL", "INFO").upper()
    logger.setLevel(level)
    logger.propagate = False

    if log_config.get("FILE", True):
        log_dir = log_config.get("DIR", "logs/output")
        os.makedirs(log_dir, exist_ok=True)
        filename = os.path.join(log_dir, "app.log")
        handler = TimedRotatingFileHandler(
            filename,
            when="midnight",
            backupCount=7,
            encoding="utf-8",
        )
        fmt = logging.Formatter(
            "%(asctime)s %(levelname)s %(process)d --- [%(threadName)s] - %(message)s"
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())
    return logger


class KafkaLog:
    def __init__(self, log_dir: str = "logs/kafka", mode: str = "a", encoding: str = "utf-8"):
        self.mode = mode
        self.log_dir = log_dir
        self.encoding = encoding
        self._suffix = ".log"
        os.makedirs(self.log_dir, exist_ok=True)
        self._base_filename = datetime.datetime.now().strftime("%Y-%m-%d")
        self._open_files()

    def _open_files(self):
        msg_filename = self._base_filename + "_msg"
        query_filename = self._base_filename + "_query"
        json_filename = self._base_filename + "_json"
        img_filename = self._base_filename + "_img"
        self.msg_filename = os.path.join(self.log_dir, msg_filename) + self._suffix
        self.query_filename = os.path.join(self.log_dir, query_filename) + self._suffix
        self.json_filename = os.path.join(self.log_dir, json_filename) + self._suffix
        self.img_filename = os.path.join(self.log_dir, img_filename) + self._suffix
        self.msg_f = open(self.msg_filename, self.mode, encoding=self.encoding)
        self.query_f = open(self.query_filename, self.mode, encoding=self.encoding)
        self.json_f = open(self.json_filename, self.mode, encoding=self.encoding)
        self.img_f = open(self.img_filename, self.mode, encoding=self.encoding)

    def _check_base_filename(self):
        cur_base = datetime.datetime.now().strftime("%Y-%m-%d")
        if cur_base != self._base_filename:
            self.msg_f.close()
            self.query_f.close()
            self.json_f.close()
            self.img_f.close()
            self._base_filename = cur_base
            self._open_files()

    def write_msg(self, msg: str):
        self._check_base_filename()
        self.msg_f.write(msg + "\n")
        self.msg_f.flush()

    def write_query(self, msg: str):
        self._check_base_filename()
        self.query_f.write(msg + "\n")
        self.query_f.flush()

    def write_json(self, msg: str):
        self._check_base_filename()
        self.json_f.write(msg + "\n")
        self.json_f.flush()

    def write_img(self, msg: str):
        self._check_base_filename()
        self.img_f.write(msg + "\n")
        self.img_f.flush()
