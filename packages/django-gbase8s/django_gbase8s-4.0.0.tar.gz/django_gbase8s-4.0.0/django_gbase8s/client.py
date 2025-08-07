import shutil
from django.db.backends.base.client import BaseDatabaseClient

class DatabaseClient(BaseDatabaseClient):
    executable_name = "dbaccess"
    wrapper_name = "rlwrap"
    
    @classmethod
    def settings_to_cmd_args_env(cls, settings_dict, parameters):
        server_name = settings_dict.get("SERVER_NAME")
        db_name = settings_dict.get("NAME")
        args = [cls.executable_name, db_name, '-']
        wrapper_path = shutil.which(cls.wrapper_name)
        if wrapper_path:
            args = [wrapper_path, *args]
        args.extend(parameters)
        return args, {'GBASEDBTSERVER': server_name}