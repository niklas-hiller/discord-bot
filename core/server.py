from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.client import Client

from core.member import Member
from core.database import Database

class Server:
    
    def __init__(self, client : "Client", server_id : int):
        self._client : "Client" = client
        self._members : list[Member] = []
        self._id : int = server_id
        
    @property
    def client(self) -> "Client":
        return self._client
        
    @property
    def database(self) -> Database:
        return self.client.database
        
    @property
    def members(self) -> list[Member]:
        return self._members
    
    @property
    def id(self) -> int:
        return self._id
    
    def new_member(self, member_id : int) -> Member:
        #print("Checking database for existing member informations")
        database_entry = self.database.read_member(member_id, self.id)
        if database_entry is None:
            #print(f"No database entry available for the member, creating new member instance ({member_id}, {self.id})")
            member = Member(
                user = self.client.retrieve_user(member_id), 
                server = self
            )
            self.database.insert_member(member)
        else:
            #print(f"Found database entry for the member, loading into new member instance ({member_id}, {self.id})")
            member = Member(
                user = self.client.retrieve_user(member_id), 
                server = self, 
                permission = database_entry['permission']
            )
        self.members.append(member)
        return member

    def retrieve_member(self, member_id : int) -> Member:
        if member_id == 0 or member_id == None: raise ValueError("Please provide a valid member id")
        for member in self.members:
            if member.id == member_id: return member
            
        #print("Couldn't retrieve member from current session, creating new member instance")
        return self.new_member(member_id)