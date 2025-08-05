import logging
import sys
from .base import Base

from pythonjsonlogger import json


class JSONLogger(Base):
	def __init__(self):
		self.__name = "logger"
		self.__pattern = "%(name)s %(asctime)s %(levelname)s %(filename)s %(lineno)s %(process)d %(message)s"
		self.__l = None
		super().__init__()

	@property
	def name(self) -> str:
		return self.name

	@name.setter
	def name(self, name: str):
		self.__name = name

	@property
	def pattern(self) -> str:
		return self.__pattern

	@pattern.setter
	def pattern(self, pattern: str):
		self.__pattern = pattern

	@property
	def l(self) -> logging.Logger:
		return self.__l

	def create_logger(self) -> None:
		stdout_handler = logging.StreamHandler(stream=sys.stdout)
		logger = logging.getLogger(self.__name)
		logger.setLevel(self.level)
		logger.addHandler(stdout_handler)
		fmt = json.JsonFormatter(self.__pattern, rename_fields={"asctime": "timestamp"})
		stdout_handler.setFormatter(fmt)
		logger.addHandler(stdout_handler)
		self.__l = logger
