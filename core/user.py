from core.enums import Auth

class User:
    """
    The global object of a discord user
    """
    
    def __init__(self, user_id : int, permission : Auth = Auth.DEFAULT):
        self._id : int = user_id
        self._permission : Auth = permission
        
    @property
    def id(self) -> int:
        return self._id
        
    @property
    def permission(self) -> Auth:
        return self._permission
    
    @permission.setter
    def permission(self, auth: Auth) -> None:
        if not isinstance(auth, Auth): raise TypeError('Please use a ``core.enums.Auth`` when overwritting the permission.')
        
        self._permission = auth