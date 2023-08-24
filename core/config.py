import yaml

from typing import Any

class Configuration:
    """
    Handles the configuration
    """
    
    @staticmethod
    def generate_template(path : str) -> None:
        data = dict(
            discord = dict(
                token = 'Your bot token',
                permission = dict(
                    moderator = ['moderator id 1', 'moderator id 2', 'moderator id 3'],
                    admin = ['admin id 1', 'admin id 2', 'admin id 3'],
                    owner = ['owner id 1', 'owner id 2', 'owner id 3']
                ),
                prefix = '.'
            )
        )

        with open(path, 'w+') as outfile:
            yaml.dump(data, outfile, default_flow_style = False)
    
    @staticmethod
    def load_yml(path : str) -> dict:
        with open(path, 'r') as stream:
            yml = yaml.safe_load(stream)
            
        return yml
    
    def update_yml(self, reference : str, value : Any) -> None:
        with open(self.path, 'r') as stream:
            yml = yaml.safe_load(stream)
            
        yml['discord'][reference] = value
            
        with open(self.path, 'w') as outfile:
            yaml.dump(yml, outfile, default_flow_style = False)
            
    
    def __init__(self, path : str = 'config.yml'):
        try:
            raw_configuration = self.__class__.load_yml(path)
        except FileNotFoundError:
            self.__class__.generate_template(path)
            raise FileNotFoundError(f"There is no such configuration file '{path}'. Generated template instead, please fill it out and retry.")
        
        self._path : str = path
        self._token : str = raw_configuration['discord']['token']
        self._permission : int = raw_configuration['discord']['permission']
        self._prefix : str = raw_configuration['discord']['prefix']
    
    @property
    def path(self) -> str:
        return self._path
    
    @path.setter
    def path(self, *args) -> RuntimeError:
        raise RuntimeError('You cannot change the configuration file path after instantiation of the configuration!')
    
    @property
    def token(self) -> str:
        return self._token
    
    @token.setter
    def token(self, token : str) -> None:
        if not isinstance(token, str): raise TypeError('Please use a ``str`` when overwritting the token.')
        self._token = token
        
    @property
    def permission(self) -> dict[str, list[int]]:
        return self._permission
    
    @permission.setter
    def permission(self, *args) -> RuntimeError:
        raise RuntimeError('Please use exclusively the configuration file to edit list of global permissions!')
    
    @property
    def prefix(self) -> str:
        return self._prefix
    
    @prefix.setter
    def prefix(self, prefix : str) -> None:
        if not isinstance(prefix, str): prefix = str(prefix)
        
        self.update_yml('prefix', prefix)
        
        self._prefix = prefix