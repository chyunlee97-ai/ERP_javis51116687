from PySide6.QtCore import QThread, Signal
from services import api_client

class ApiQueryThread(QThread):
    # Signal to emit when API call finishes, returning the response dict
    finished_signal = Signal(object)
    
    def __init__(self, message: str = "", intent: str = None, fact: str = None, as_find: str = None, limit: int = 50, offset: int = 0):
        super().__init__()
        self.message = message
        self.intent = intent
        self.fact = fact
        self.as_find = as_find
        self.limit = limit
        self.offset = offset
        
    def run(self):
        # Call the API service in the background
        response = api_client.ask(
            message=self.message,
            intent=self.intent,
            fact=self.fact,
            as_find=self.as_find,
            limit=self.limit,
            offset=self.offset
        )
        # Emit the result back to the main UI thread
        self.finished_signal.emit(response)
