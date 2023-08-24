import discord

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.server import Server

from core.enums import Auth
from core.user import User

class Member:
    """
    The server object of a discord user
    """
    
    def __init__(self, user : User, server : "Server", permission : Auth = Auth.DEFAULT):
        self._user : User = user
        self._server : "Server" = server
        self._permission : Auth = permission
        
    @property
    def id(self) -> int:
        return self.user.id
        
    @property
    def user(self) -> User:
        return self._user
    
    @property
    def server(self) -> "Server":
        return self._server
        
    @property
    def permission(self) -> Auth:
        return self._permission if self.user.permission.value < self._permission.value else self.user.permission
    
    @permission.setter
    def permission(self, auth: Auth) -> None:
        if not isinstance(auth, Auth): raise TypeError('Please use a ``core.enums.Auth`` when overwritting the permission.')
        
        self.server.database.update_member(self, 'permission', auth.value)
        self._permission = auth
        
    def has_permission(self, permission: Auth) -> bool:
        return self.permission.value >= permission.value
    
    