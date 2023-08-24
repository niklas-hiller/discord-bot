import threading

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.client import Client

class ClientThread(threading.Thread):
    
    def __init__(self, client : "Client", *args, **kwargs):
        super().__init__()
        self._client : "Client" = client
    
    @property
    def client(self) -> "Client":
        return self._client
    
    def run(self):
        self.client._run()
    
    def get_id(self):
        if hasattr(self, "_thread_id"):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
            