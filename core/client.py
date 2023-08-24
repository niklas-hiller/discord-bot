import discord

from typing import Awaitable, Union

from core.config import Configuration
from core.console import Console
from core.enums import Auth, Event, Restriction
from core.event import Events
from core.server import Server
from core.user import User
from core.database import Database
from core.thread import ClientThread
from core.music import Music
from core.audio_receiver import GoogleSpeechToText, BufferAudioSink


class Client(discord.Client):
    """
    Extends the discord.py client
    """
    
    def __init__(self, config : Configuration = None, music_path : str = None):
        super().__init__()

        self._config : Configuration = config
        self._running : bool = False
        self._users : list[User] = []
        self._servers : list[Server] = []
        self._database : Database = None
        self._is_ready : bool = False
        self._thread : ClientThread = None
        self._transcriber : GoogleSpeechToText = GoogleSpeechToText(
            recognition_model = 'phone_call', 
            lang = 'de-DE', 
            api_credentials = args.google_api_credentials_file
        )
        self._audio_sink : BufferAudioSink = BufferAudioSink(self.transcribe)
        
        self._events : Events = Events(self)
        
        self._music : Music = Music()
        if music_path is not None: self.music.read(music_path)
        
        @self.event
        async def on_ready():
            print(f'Sucessfully logged in as {self.user}')
            self._is_ready = True
            
        @self.event
        async def on_message(message : discord.Message):
            if message.author == self.user:
                return
            
            await self._events.process(Event.ON_MESSAGE, message, False)

            if message.content.startswith(self.prefix):
                await self._events.process(Event.ON_COMMAND, message, prefix = self.prefix)
                
            await self._events.process(Event.ON_MESSAGE, message, True)
            
        @self.event
        async def on_reaction_add(reaction : discord.Reaction, user : Union[discord.Member, discord.User]):
            await self._events.process(Event.ON_REACTION_ADD, reaction, user)
            
        # @self.event
        # async def on_reaction_remove(reaction : discord.Reaction, user : Union[discord.Member, discord.User]):
        #     await self._events.process(Event.ON_REACTION_REMOVE, reaction, user, False)
        
        @self.event
        async def on_member_join(member : discord.Member):
            await self._events.process(Event.ON_MEMBER_JOIN, member)
            
        @self.event
        async def on_member_remove(member : discord.Member):
            await self._events.process(Event.ON_MEMBER_REMOVE, member)
                
        @self.react(Event.ON_COMMAND, 'permission', permission = Auth.DEFAULT)
        async def retrieve_authorization_command(message : discord.Message):
            await message.reply(f'Your authorization level is ``{self.retrieve_server(message.guild.id).retrieve_member(message.author.id).permission.name.lower()}``')
          
    # For Voice Recognition Feature
    def transcribe(self, speaker, pcm_s16le, sample_rate, num_channels):
        hyp = self.transcriber.transcribe(pcm_s16le, sample_rate, num_channels)
        print('Transcribing', '[', hyp, ']')
        if hyp:
            self.messages.append((speaker, hyp))
          
    @property
    def events(self) -> Events:
        return self._events
          
    def react(self, event_type : Event, *args, **kwargs):
        def decorator(coro : Awaitable[None]):
            self.events.add(
                coro,
                event_type,
                *args,
                **kwargs
            )
            
            return coro

        return decorator
        
    @property
    def music(self) -> Music:
        return self._music
        
    @property
    def database(self) -> Database:
        return self._database
        
    @property
    def users(self) -> list[User]:
        return self._users
    
    @property
    def servers(self) -> list[Server]:
        return self._servers
        
    @property
    def running(self) -> bool:
        return self._running
        
    @property
    def config(self) -> Configuration:
        return self._config
    
    @property
    def is_ready(self) -> bool:
        return self._is_ready
    
    @config.setter
    def config(self, config: Configuration) -> None:
        if self.running: raise RuntimeError('You cannot change the configuration while the application is running!')
        if not isinstance(config, Configuration): raise TypeError('Please use a ``core.config.Configuration`` when overwritting a config.')
        self._config = config
        
    @property
    def token(self) -> str: 
        return self.config.token

    @token.setter
    def token(self, token : str): 
        self.config.token = token
    
    @property
    def prefix(self) -> str: 
        return self.config.prefix

    @prefix.setter
    def prefix(self, prefix : str): 
        self.config.prefix = prefix
    
    def retrieve_server(self, server_id : int) -> Server:
        if server_id == 0 or server_id == None: raise ValueError("Please provide a valid server id")
        for server in self.servers:
            if server.id == server_id: return server
            
        server = Server(self, server_id)
        self.servers.append(server)
        return server
    
    def retrieve_user(self, user_id : int):
        if user_id == 0 or user_id == None: raise ValueError("Please provide a valid user id")
        for user in self.users:
            if user.id == user_id: return user
            
        return self.new_user(user_id)
    
    def new_user(self, user_id : int, permission : Auth = Auth.DEFAULT):
        if user_id == 0 or user_id == None: raise ValueError("Please provide a valid user id")
        for user in self.users:
            if user.id == user_id: raise RuntimeError(f"The user with id '{user_id}' already exists!")
            
        user = User(user_id, permission = permission)
        self.users.append(user)
        return user
        
    def _run(self):
        if self.running: raise RuntimeError('You cannot run a running application!')
        if self.token is None: raise KeyError('There was no token provided in configuration')
        
        self._database = Database()
        
        for permission, user_ids in self.config.permission.items():
            for user_id in user_ids:
                try:
                    self.new_user(user_id, permission = Auth.convert(permission))
                except RuntimeError:
                    raise ValueError(f"You can't have multiple permissions assigned to one user in your {self.config.path}")
        
        self._running = True
        
        super().run(self.token)
        
    def run(self, threaded : bool = False, access_console : Console = None) -> "Client":
        if threaded and access_console: UserWarning('Running the bot threaded is redundant when bot is ran with console access')
        
        if threaded or access_console:
            self._thread : ClientThread = ClientThread(self)
            self._thread.daemon = True
            self._thread.start()
        else:
            self._run()
            
        if access_console:
            if not self.is_ready: print("Please wait while bot is starting...")
            while not self.is_ready: pass
            while True:
                try:
                    user_input = input('>>> ')
                    access_console.process(self, user_input)
                except KeyboardInterrupt:
                    raise KeyboardInterrupt('The program was interrupted by user.')
        
        return self
    
        