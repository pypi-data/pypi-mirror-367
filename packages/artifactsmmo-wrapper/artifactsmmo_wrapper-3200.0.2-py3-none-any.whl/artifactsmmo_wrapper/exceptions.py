from typing import Optional
from .log import logger
import traceback

# --- Exceptions ---
class APIException(Exception):
    """Enhanced base exception class for API errors with better tracking."""
    
    def __init__(self, message: str, char_name: Optional[str] = "ROOT"):
        super().__init__(message)
        self.char_name = char_name
        self.traceback = traceback.format_exc()
        self._log_error(message)
    
    def _log_error(self, message: str) -> None:
        """Log error with traceback information."""
        logger.error(
            f"{self.__class__.__name__}: {message}\nTraceback:\n{self.traceback}",
            extra={"char": self.char_name}
        )

    class CharacterInCooldown(Exception):
        def __init__(self, message="Character is in cooldown"):
            super().__init__(message)
            logger.warning(f"CharacterInCooldown: {message}", src="Root")

    class NotFound(Exception):
        def __init__(self, message="Resource not found"):
            super().__init__(message)
            logger.error(f"NotFound: {message}", src="Root")

    class ActionAlreadyInProgress(Exception):
        def __init__(self, message="Action is already in progress"):
            super().__init__(message)
            logger.warning(f"ActionAlreadyInProgress: {message}", src="Root")

    class CharacterNotFound(Exception):
        def __init__(self, message="Character not found"):
            super().__init__(message)
            logger.error(f"CharacterNotFound: {message}", src="Root")

    class TooLowLevel(Exception):
        def __init__(self, message="Level is too low"):
            super().__init__(message)
            logger.error(f"TooLowLevel: {message}", src="Root")

    class InventoryFull(Exception):
        def __init__(self, message="Inventory is full"):
            super().__init__(message)
            logger.warning(f"InventoryFull: {message}", src="Root")

    class MapItemNotFound(Exception):
        def __init__(self, message="Map item not found"):
            super().__init__(message)
            logger.error(f"MapItemNotFound: {message}", src="Root")

    class InsufficientQuantity(Exception):
        def __init__(self, message="Insufficient quantity"):
            super().__init__(message)
            logger.warning(f"InsufficientQuantity: {message}", src="Root")

    class GETooMany(Exception):
        def __init__(self, message="Too many GE items"):
            super().__init__(message)
            logger.error(f"GETooMany: {message}", src="Root")

    class GENoStock(Exception):
        def __init__(self, message="No stock available"):
            super().__init__(message)
            logger.error(f"GENoStock: {message}", src="Root")

    class GENoItem(Exception):
        def __init__(self, message="Item not found in GE"):
            super().__init__(message)
            logger.error(f"GENoItem: {message}", src="Root")

    class TransactionInProgress(Exception):
        def __init__(self, message="Transaction already in progress"):
            super().__init__(message)
            logger.warning(f"TransactionInProgress: {message}", src="Root")

    class InsufficientGold(Exception):
        def __init__(self, message="Not enough gold"):
            super().__init__(message)
            logger.warning(f"InsufficientGold: {message}", src="Root")

    class TaskMasterNoTask(Exception):
        def __init__(self, message="No task assigned to TaskMaster"):
            super().__init__(message)
            logger.error(f"TaskMasterNoTask: {message}", src="Root")

    class TaskMasterAlreadyHasTask(Exception):
        def __init__(self, message="TaskMaster already has a task"):
            super().__init__(message)
            logger.warning(f"TaskMasterAlreadyHasTask: {message}", src="Root")

    class TaskMasterTaskNotComplete(Exception):
        def __init__(self, message="TaskMaster task is not complete"):
            super().__init__(message)
            logger.error(f"TaskMasterTaskNotComplete: {message}", src="Root")

    class TaskMasterTaskMissing(Exception):
        def __init__(self, message="TaskMaster task is missing"):
            super().__init__(message)
            logger.error(f"TaskMasterTaskMissing: {message}", src="Root")

    class TaskMasterTaskAlreadyCompleted(Exception):
        def __init__(self, message="TaskMaster task already completed"):
            super().__init__(message)
            logger.warning(f"TaskMasterTaskAlreadyCompleted: {message}", src="Root")

    class RecyclingItemNotRecyclable(Exception):
        def __init__(self, message="Item is not recyclable"):
            super().__init__(message)
            logger.error(f"RecyclingItemNotRecyclable: {message}", src="Root")

    class EquipmentTooMany(Exception):
        def __init__(self, message="Too many equipment items"):
            super().__init__(message)
            logger.warning(f"EquipmentTooMany: {message}", src="Root")

    class EquipmentAlreadyEquipped(Exception):
        def __init__(self, message="Equipment already equipped"):
            super().__init__(message)
            logger.warning(f"EquipmentAlreadyEquipped: {message}", src="Root")

    class EquipmentSlot(Exception):
        def __init__(self, message="Invalid equipment slot"):
            super().__init__(message)
            logger.error(f"EquipmentSlot: {message}", src="Root")

    class AlreadyAtDestination(Exception):
        def __init__(self, message="Already at destination"):
            super().__init__(message)
            logger.info(f"AlreadyAtDestination: {message}", src="Root")

    class BankFull(Exception):
        def __init__(self, message="Bank is full"):
            super().__init__(message)
            logger.warning(f"BankFull: {message}", src="Root")

    class TokenMissingorEmpty(Exception):
        def __init__(self, message="Token is missing or empty"):
            super().__init__(message)
            logger.critical(f"TokenMissingorEmpty: {message}", src="Root")
            exit(1)
                
    class NameAlreadyUsed(Exception):
        def __init__(self, message="Name already used"):
            super().__init__(message)
            logger.error(f"NameAlreadyUsed: {message}", src="Root")
    
    class MaxCharactersReached(Exception):
        def __init__(self, message="Max characters reached"):
            super().__init__(message)
            logger.warning(f"MaxCharactersReached: {message}", src="Root")

