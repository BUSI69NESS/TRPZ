import logging
from abc import ABC, abstractmethod
from datetime import datetime
from MusicPlayer.server.core.config import log_file_path


class CommandVisitor(ABC):
    @abstractmethod
    def visit_save_memento(self, command):
        pass

    @abstractmethod
    def visit_restore_memento(self, command):
        pass

class LoggingVisitor(CommandVisitor):
    def __init__(self):
        logging.basicConfig(filename=log_file_path, level=logging.INFO)

    def visit_save_memento(self, command):
        logging.info(f"SaveMementoCommand executed at {datetime.now()}")

    def visit_restore_memento(self, command):
        logging.info(f"RestoreMementoCommand executed at {datetime.now()}")