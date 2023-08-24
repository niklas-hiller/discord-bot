import glob, uuid, os, json, random, difflib, hashlib

class Track:
    
    def __init__(self, name : str, path : str, description : str = "", reference : uuid.UUID = None):
        self._reference = reference or uuid.uuid4()
        self._name = name
        self._description = description
        self._path = path
        self._hash = self.md5().hexdigest()
    
    @property
    def reference(self) -> uuid.UUID:
        return self._reference
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def path(self) -> str:
        return self._path
    
    @property
    def hash(self) -> str:
        return self._hash

    def __eq__(self, track : "Track") -> bool:
        if not isinstance(track, Track): return False
        return self.hash == track.hash
    
    def __ne__(self, track : "Track") -> bool:
        return not self.__eq__(track)
    
    def md5(self) -> "hashlib._Hash":
        hash_md5 = hashlib.md5()
        with open(self.path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5
    
    def to_dict(self) -> dict:
        print(f"Converting {self} to dictionary")
        return {
            "reference": self.reference.hex,
            "name": self.name,
            "description": self.description,
            "path": self.path,
            "checksum": self.hash
        }
    
    @staticmethod
    def construct(data : dict) -> "Track":
        return Track(
            name = data['name'],
            description = data['description'],
            path = data['path'],
            reference = uuid.UUID(data["reference"])
        )

class Playlist:
    
    def __init__(self, name : str, description : str = "", tracks : list[Track] = [], reference : uuid.UUID = None):
        self._reference = reference or uuid.uuid4()
        self._name = name
        self._description = description
        self._tracks = tracks
    
    @property
    def reference(self) -> uuid.UUID:
        return self._reference
        
    @property
    def name(self) -> str:
        return self._name
        
    @property
    def description(self) -> str:
        return self._description
        
    @property
    def tracks(self) -> list[Track]:
        if any(not isinstance(track, Track) for track in self._tracks): raise RuntimeWarning("This playlist contains unloaded tracks, it might cause problems if a track is used before loaded!")
        return self._tracks
    
    def __eq__(self, playlist : "Playlist") -> bool:
        if not isinstance(playlist, Playlist): return False
        return all(
            any(
                _track == track
                for _track in self.tracks
            )
            for track in playlist.tracks
        )
    
    def __ne__(self, playlist : "Playlist") -> bool:
        return not self.__eq__(playlist)
    
    def random_track(self) -> Track:
        return random.choice(self.tracks)
    
    def to_dict(self) -> dict:
        print(f"Converting {self} to dictionary")
        return {
            "reference": self.reference.hex,
            "name": self.name,
            "description": self.description,
            "tracks": [track.reference.hex for track in self.tracks]
        }
    
    def load(self, tracks : list[Track]):
        update = []
        for track in self._tracks:
            if isinstance(track, uuid.UUID):
                found = None
                for _track in tracks:
                    if _track.reference == track:
                        found = _track
                        break
                if found is not None:
                    update.append(found)
                    continue
            update.append(track)
        self._tracks = update
    
    @staticmethod
    def construct(data : dict) -> "Playlist":
        return Playlist(
            name = data['name'],
            description = data['description'],
            reference = uuid.UUID(data["reference"]),
            tracks = [uuid.UUID(track) for track in data["tracks"]]
        )
        
            
class Music:
    
    def __init__(self, playlists : list[Playlist] = [], tracks : list[Track] = []):
        self._playlists = playlists
        
        # Load missing tracks from playlists into tracklist
        print("Checking for missing tracks in playlist")
        for playlist in playlists:
            for track in playlist.tracks:
                if not isinstance(track, Track): continue
                if track not in tracks:
                    print("Detected a track in playlist that is missing in tracklist, copying into tracks list")
                    tracks.append(track)
                    
        self._tracks = tracks

        print("Loading unloaded tracks into playlist")
        for playlist in self.playlists: 
            playlist.load(self.tracks)
        print("Finished loading unloaded tracks")
        
    @property
    def playlists(self) -> list[Playlist]:
        return self._playlists
    
    @property
    def tracks(self) -> list[Track]:
        return self._tracks
    
    def random_track(self) -> Track:
        return random.choice(self.tracks)
    
    def random_playlist(self) -> Playlist:
        return random.choice(self.playlists)
    
    def search_track(self, title : str) -> Track:
        if len(self.tracks) == 0: return
        min_diff = (0,0)
        for track in self.tracks:
            curr_diff = difflib.SequenceMatcher(None, title, track.name).ratio()
            if curr_diff > min_diff[0]:
                min_diff = (curr_diff, track)
        return min_diff[1]
    
    def search_playlist(self, title : str) -> Playlist:
        if len(self.playlists) == 0: return
        min_diff = (0,0)
        for playlist in self.playlists:
            curr_diff = difflib.SequenceMatcher(None, title, playlist.name).ratio()
            if curr_diff > min_diff[0]:
                min_diff = (curr_diff, playlist)
        return min_diff[1]
    
    def append(self, obj : Track | Playlist):
        if not (isinstance(obj, Track) or isinstance(obj, Playlist)): raise TypeError("You can only append Tracks or Playlists to Music objects")
        
        if isinstance(obj, Track):
            if any(track.reference == obj.reference for track in self.tracks): return
            if any(track == obj for track in self.tracks): return
            self.tracks.append(obj)
        elif isinstance(obj, Playlist):
            if any(playlist.reference == obj.reference for playlist in self.playlists): return
            if any(playlist == obj for playlist in self.playlists): return
            self.playlists.append(obj)
    
    def to_dict(self) -> dict:
        return {
            "playlists": [playlist.to_dict() for playlist in self.playlists],
            "tracks": [track.to_dict() for track in self.tracks]
        }
    
    def save(self, path : str):
        with open(f"{path}\\index.json", "w+") as index_file:
            json.dump(self.to_dict(), index_file, indent = 4)
            
    def read(self, path : str):
        try:
            with open(f"{path}\\index.json", "r") as index_file:
                data = json.load(index_file)
        except FileNotFoundError:
            print("No index file found at path, please do a scan in console...")
            return
        except json.decoder.JSONDecodeError:
            print("Invalid json structure, please fix manually or scan new...")
            return
            
        for track in data['tracks']:
            self.append(Track.construct(track))
            
        for playlist in data['playlists']:
            self.append(Playlist.construct(playlist))
            
        for playlist in self.playlists: 
            playlist.load(self.tracks)
    
    def merge(self, music : "Music") -> "Music":
        if not isinstance(music, Music): raise TypeError("You can only merge Music objects with other Music objects")
        
        for track in music.tracks:
            self.append(track)
            
        for playlist in music.playlists:
            self.append(playlist)
            
        for playlist in self.playlists: 
            playlist.load(self.tracks)
        
        return self
    
    @staticmethod
    def scan(path : str) -> "Music":
        scanned_tracks = [f for f in glob.glob(f"{path}\\*.mp3")]
        tracks = []
        
        for track in scanned_tracks:
            tracks.append(
                Track(
                    name = os.path.splitext(os.path.basename(track))[0],
                    path = track,
                    description = "",
                    reference = uuid.uuid4()
                )
            )
        print(f"Detected {len(tracks)} tracks in '{path}'.")
        
        playlist = Playlist(
            name = f"music of {path}",
            description = f"This is a playlist containing all scanned .mp3 files in {path}",
            tracks = tracks,
            reference = uuid.uuid4()
        )
            
        return Music([playlist], tracks)