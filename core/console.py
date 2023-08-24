import asyncio
from typing import TYPE_CHECKING, Awaitable, Callable

if TYPE_CHECKING:
    from core.client import Client


class Console:
    
    def __init__(self):
        self.client = None
        self.functions = {}
    
    def process(self, client : "Client", user_input : str) -> None:
        if user_input == "": return
        
        raw_args = user_input.split(" ")
        
        command = raw_args[0]
        args = []
        if len(raw_args) > 1:
            args = tuple(raw_args[1:])
                
        if command not in self.functions: 
            print(f"There is no '{command}' command.")
            return
                
        args = tuple(args)

        try:
            if asyncio.iscoroutinefunction(self.functions[command]):
                client.loop.create_task(self.functions[command](*args))
            else:
                self.functions[command](*args)
        except TypeError as e:
            print(e)
    
    def func(self, command : str):
        def decorator(callback : Awaitable[None] | Callable):
            self.functions[command] = callback
            
            return callback

        return decorator