import logging
import re
from abc import ABC, abstractmethod


class Base(ABC):

	def __init__(self):
		self.__level = None
	@property
	@abstractmethod
	def name(self) -> str :
		pass
	@name.setter
	@abstractmethod
	def name(self, name: str) -> None:
		pass
	@property
	def level(self) -> str:
		return self.__level
	@level.setter
	def level(self, level: str):
		if re.match(r"(?i)(NOTSET|DEBUG|INFO|WARNING|ERROR|CRITICAL)", level):
			self.__level = level.upper()
		else:
			raise ValueError("Invalid log level")
	@property
	@abstractmethod
	def pattern(self) -> str:
		pass
	@pattern.setter
	@abstractmethod
	def pattern(self, pattern: str) -> None:
		pass
	@property
	@abstractmethod
	def l(self) -> logging.Logger:
		pass
	@abstractmethod
	def create_logger(self) -> None:
		pass