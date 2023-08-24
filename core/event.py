import asyncio, discord

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Awaitable, Union
from core.enums import Auth, Restriction, Event

if TYPE_CHECKING:
    from core.client import Client


class Single(ABC):
        
    def __init__(self, coro : Awaitable[None]):
        self._coroutine : Awaitable[None] = coro
        
    @property
    def coroutine(self) -> Awaitable[None]:
        return self._coroutine
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> None:
        # do conditional stuff here
        await self.coroutine(*args, **kwargs)
    
    
class Member_Event(Single):
    
    def __init__(self, coro : Awaitable[None]):
        super().__init__(coro)
        
    async def execute(self, client : "Client", member : discord.Member) -> None:
        await super().execute(member)


class Reaction_Event(Single):
    
    def __init__(self, coro : Awaitable[None]):
        super().__init__(coro)
        
    async def execute(self, client : "Client", reaction : discord.Reaction, user : Union[discord.Member, discord.User]) -> None:
        await super().execute(reaction, user)


class Message_Event(Single):
    
    def __init__(self, coro : Awaitable[None], restriction : Restriction = Restriction.NONE, after_command : bool = False):
        super().__init__(coro)
        
        self.restriction : Restriction = restriction
        self.after_command : bool = after_command
        
    async def execute(self, client : "Client", message : discord.Message, after_command : bool) -> None:
        if not after_command == self.after_command: return
        
        await super().execute(message)


class Command_Event(Single):
    
    def __init__(self, coro : Awaitable[None], command : str, permission : Auth = Auth.DEFAULT, restriction : Restriction = Restriction.NONE, requires_voice : bool = False):
        super().__init__(coro)

        self.command : str = command
        self.permission : Auth = permission
        self.restriction : Restriction = restriction
        self.requires_voice : bool = requires_voice
        
    async def execute(self, client : "Client", message : discord.Message, prefix : str) -> None:
        if not message.content.startswith(f'{prefix}{self.command}'): return
        
        await message.channel.trigger_typing()
        if not client.retrieve_server(message.guild.id).retrieve_member(message.author.id).has_permission(self.permission):
            await message.channel.send("You don't have the necessary permission to use this command.")
            return
        if self.restriction != Restriction.NONE and message.channel.is_nsfw():
            await message.channel.send("You are not allowed to use this command outside of a NSFW channel.")
            return
        if self.requires_voice and message.guild.voice_client is None:
            await message.reply(f"I'm required to be connected to a voice channel for this action.")
            return
        await super().execute(message, *tuple(message.content[len(prefix) + len(self.command) + 1:].split(" ")))
    
    
class Collection:
    
    def __init__(self, client : "Client"):
        self._client : "Client" = client
        self._events : list[Single] = []
        
    @property
    def client(self) -> "Client":
        return self._client
        
    @property
    def events(self) -> list[Single]:
        return self._events
    
    async def process(self, *args, **kwargs) -> "Collection":
        for event in self.events:
            await event.execute(self.client, *args, **kwargs)
            
        return self
    
    def add(self, coro : Awaitable[None], event_type : Event, *args, **kwargs) -> "Collection":
        if not isinstance(event_type, Event): raise TypeError(f"{event_type.__type__} is unequal {Event}.")
        
        match event_type:
            case Event.ON_MESSAGE:
                self.events.append(
                    Message_Event(coro, *args, **kwargs)
                )
            case Event.ON_COMMAND:
                self.events.append(
                    Command_Event(coro, *args, **kwargs)
                )
            case Event.ON_REACTION_ADD:
                self.events.append(
                    Reaction_Event(coro, *args, **kwargs)
                )
            case Event.ON_REACTION_REMOVE:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_MEMBER_JOIN:
                self.events.append(
                    Member_Event(coro, *args, **kwargs)
                )
            case Event.ON_MEMBER_REMOVE:
                self.events.append(
                    Member_Event(coro, *args, **kwargs)
                )
            case Event.ON_MESSAGE_DELETE:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_MESSAGE_EDIT:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_MEMBER_UPDATE:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_USER_UPDATE:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_GUILD_JOIN:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_GUILD_REMOVE:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_GUILD_UPDATE:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_MEMBER_BAN:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_MEMBER_UNBAN:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case _:
                raise ValueError(f"The event {event_type} is unknown. Please check ``core.enums.Event`` for further informations")
                
        return self


class Events:
    
    def __init__(self, client : "Client"):
        self._values : dict[Event, Collection] = {
            Event.ON_MESSAGE: Collection(client),
            Event.ON_COMMAND: Collection(client),
            Event.ON_REACTION_ADD: Collection(client),
            Event.ON_REACTION_REMOVE: Collection(client),
            Event.ON_MEMBER_JOIN: Collection(client),
            Event.ON_MEMBER_REMOVE: Collection(client),
            Event.ON_MESSAGE_DELETE: Collection(client),
            Event.ON_MESSAGE_EDIT: Collection(client),
            Event.ON_MEMBER_UPDATE: Collection(client),
            Event.ON_USER_UPDATE: Collection(client),
            Event.ON_GUILD_JOIN: Collection(client),
            Event.ON_GUILD_REMOVE: Collection(client),
            Event.ON_GUILD_UPDATE: Collection(client),
            Event.ON_MEMBER_BAN: Collection(client),
            Event.ON_MEMBER_UNBAN: Collection(client)
        }
        
    @property
    def values(self):
        return self._values
        
    async def process(self, event_type : Event, *args, **kwargs) -> "Events":
        if event_type not in self.values: raise ValueError(f'The event type {event_type} does not exist')

        await self.values[event_type].process(*args, **kwargs)
        
        return self
        
    def add(self, coro : Awaitable[None], event_type : Event, *args, **kwargs):
        if not asyncio.iscoroutinefunction(coro): raise TypeError('Event registered must be a coroutine function')
        if not isinstance(event_type, Event): raise TypeError(f"{event_type.__type__} is unequal {Event}.")

        match event_type:
            case Event.ON_COMMAND:
                '''
                permission : Auth = Auth.DEFAULT
                restriction : Restriction = Restriction.NONE
                
                message : discord.Message
                '''
                self.values[Event.ON_COMMAND].add(
                    coro,
                    Event.ON_COMMAND,
                    *args,
                    **kwargs
                )
            case Event.ON_MESSAGE:
                '''
                after_command : bool = False
                
                message : discord.Message
                '''
                self.values[Event.ON_MESSAGE].add(
                    coro,
                    Event.ON_MESSAGE,
                    *args,
                    **kwargs
                )
            case Event.ON_REACTION_ADD:
                '''
                None
                
                reaction : discord.Reaction
                user : Union[discord.Member, discord.User]
                '''
                self.values[Event.ON_REACTION_ADD].add(
                    coro,
                    Event.ON_REACTION_ADD,
                    *args,
                    **kwargs
                )
            case Event.ON_REACTION_REMOVE:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_MEMBER_JOIN:
                '''
                None
                
                member : discord.Member
                '''
                self.values[Event.ON_MEMBER_JOIN].add(
                    coro,
                    Event.ON_MEMBER_JOIN,
                    *args,
                    **kwargs
                )
            case Event.ON_MEMBER_REMOVE:
                '''
                None
                
                member : discord.Member
                '''
                self.values[Event.ON_MEMBER_REMOVE].add(
                    coro,
                    Event.ON_MEMBER_REMOVE,
                    *args,
                    **kwargs
                )
            case Event.ON_MESSAGE_DELETE:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_MESSAGE_EDIT:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_MEMBER_UPDATE:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_USER_UPDATE:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_GUILD_JOIN:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_GUILD_REMOVE:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_GUILD_UPDATE:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_MEMBER_BAN:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case Event.ON_MEMBER_UNBAN:
                raise NotImplementedError(f"The event '{event_type.name}' is not implemented yet")
            case _:
                raise ValueError(f"The event {event_type} is unknown. Please check ``core.enums.Event`` for further informations")
            
        print(f'{coro.__name__} has successfully been registered as an {event_type.name}')