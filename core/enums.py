from enum import Enum, auto

class Event(Enum):
    ON_MESSAGE = auto()
    ON_COMMAND = auto()
    ON_REACTION_ADD = auto()
    ON_REACTION_REMOVE = auto() # Not implemented yet
    ON_MEMBER_JOIN = auto()
    ON_MEMBER_REMOVE = auto()
    
    # Not implemented yet
    ON_MESSAGE_DELETE = auto()
    ON_MESSAGE_EDIT = auto()
    ON_MEMBER_UPDATE = auto()
    ON_USER_UPDATE = auto()
    ON_GUILD_JOIN = auto()
    ON_GUILD_REMOVE = auto()
    ON_GUILD_UPDATE = auto()
    ON_MEMBER_BAN = auto()
    ON_MEMBER_UNBAN = auto()
    

class Restriction(Enum):
    NONE = 0
    NSFW = 1
    
    @staticmethod
    def convert(restriction : int | str) -> "Restriction":
        if isinstance(restriction, Restriction): return restriction
        if not isinstance(restriction, int) and not isinstance(restriction, str): raise TypeError('Please use a ``int`` or ``str`` for restriction level conversion.')
        
        try:
            restriction = int(restriction)
        except ValueError:
            restriction = restriction
        restriction = restriction.upper() if isinstance(restriction, str) else restriction
        
        match restriction:
            case Restriction.NONE.value | Restriction.NONE.name:
                return Restriction.NONE
            case Restriction.NSFW.value | Restriction.NSFW.name:
                return Restriction.NSFW
            case _:
                raise ValueError(f"The restriction level {restriction} is unknown. Please check ``core.enums.Restriction`` for further informations")
            

class Auth(Enum):
    DEFAULT = 0
    MODERATOR = 1
    ADMIN = 2
    OWNER = 3
    
    @staticmethod
    def convert(auth : int | str) -> "Auth":
        if isinstance(auth, Auth): return auth
        if not isinstance(auth, int) and not isinstance(auth, str): raise TypeError('Please use a ``int`` or ``str`` for auth level conversion.')
        
        try:
            auth = int(auth)
        except ValueError:
            auth = auth
        auth = auth.upper() if isinstance(auth, str) else auth
        
        match auth:
            case Auth.DEFAULT.value | Auth.DEFAULT.name:
                return Auth.DEFAULT
            case Auth.MODERATOR.value | Auth.MODERATOR.name:
                return Auth.MODERATOR
            case Auth.ADMIN.value | Auth.ADMIN.name:
                return Auth.ADMIN
            case Auth.OWNER.value | Auth.OWNER.name:
                return Auth.OWNER
            case _:
                raise ValueError(f"The auth level {auth} is unknown. Please check ``core.enums.Auth`` for further informations")