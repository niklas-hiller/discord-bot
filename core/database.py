import sqlite3

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.member import Member

from core.enums import Auth

class Database:
    
    def __init__(self):
        self._connection : sqlite3.Connection = sqlite3.connect('.sqlite')
        self._cursor : sqlite3.Cursor = self.connection.cursor()
        
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS members
                            ([user_id] INTEGER NOT NULL, [server_id] INTEGER NOT NULL, [permission] INTEGER NOT NULL, PRIMARY KEY (user_id, server_id))
                            ''')
        
        self.connection.commit()

    @property
    def connection(self) -> sqlite3.Connection:
        return self._connection
    
    @property
    def cursor(self) -> sqlite3.Cursor:
        return self._cursor
        
    def insert_member(self, member : "Member"):
        self.cursor.execute(f'''
                            INSERT INTO members (user_id, server_id, permission)

                                    VALUES
                                    ({member.user.id},{member.server.id},{member._permission.value})
                            ''')
        
        self.connection.commit()
        
    def update_member(self, member : "Member", key : str, value):
        # print(f"Updating {member} key '{key}' to '{value}'")
        self.cursor.execute(f'''
                            UPDATE members

                            SET {key} = {value}
                            WHERE user_id = {member.user.id}
                            AND server_id = {member.server.id}
                            ''')
        
        self.connection.commit()
        
    def read_member(self, user_id : int, server_id : int) -> dict:
        self.cursor.execute(f'''
                            SELECT * FROM members
                            WHERE user_id = {user_id}
                            AND server_id = {server_id}
                            ''')
        rows = self.cursor.fetchall()
        
        if len(rows) == 0:
            return None
        assert len(rows) == 1, "CORRUPTED DATABASE: There were more than one member with the same user id and same server id!"

        database_entry = dict(
            user_id = rows[0][0],
            server_id = rows[0][1],
            permission = Auth.convert(rows[0][2])
        )
        return database_entry
        
    def read_members(self) -> list[dict]:
        self.cursor.execute(f'''
                            SELECT * FROM members
                            ''')
        rows = self.cursor.fetchall()
        
        database_entries = []
        for row in rows:
            database_entry = dict(
                user_id = row[0],
                server_id = row[1],
                permission = Auth.convert(row[2])
            )
            database_entries.append(database_entry)
        
        return database_entries