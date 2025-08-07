import datetime
import warnings
from .base import Database
from django.utils import timezone
from django.conf import settings

def dsn(settings_dict):  
    params = {
        "server_name": settings_dict["SERVER_NAME"],
        "db_name": settings_dict["NAME"],
        "host": settings_dict.get("HOST", None),
        "port": settings_dict.get("PORT", None),
    }  
    
    if settings_dict.get("PROTOCOL"):
        params['protocol'] = settings_dict.get("PROTOCOL")
    if settings_dict.get("DB_LOCALE"):
        params['db_locale'] = settings_dict.get("DB_LOCALE")
    if settings_dict.get("CLIENT_LOCALE"):
        params['client_locale'] = settings_dict.get("CLIENT_LOCALE")
    if settings_dict.get("SQLH_FILE"):
        params['sqlh_file'] = settings_dict.get("SQLH_FILE")

    return Database.makedsn(**params)

class GBase8s_datetime(datetime.datetime):

    input_size = Database.DB_TYPE_TIMESTAMP

    @classmethod
    def from_datetime(cls, dt):
        return GBase8s_datetime(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
        )
        
    @classmethod
    def from_date(cls, dt):
        return GBase8s_datetime(
            dt.year,
            dt.month,
            dt.day,
        )
        
        
class GBase8s_date(datetime.date):

    input_size = Database.DB_TYPE_DATE
        
    @classmethod
    def from_date(cls, dt):
        return GBase8s_date(
            dt.year,
            dt.month,
            dt.day,
        )
        
        
class GBase8sParam:

    def __init__(self, param):
        if isinstance(param, GBase8sParam):
            self._input_size = param.input_size
            self._param = param.param
            return
        self._input_size = None
        self._param = param
        if isinstance(param, datetime.datetime) and not isinstance(param, GBase8s_datetime):
            self._param = GBase8s_datetime.from_datetime(param)
            self._input_size = self._param.input_size
        elif param == '':
            self._param = None

    @property
    def param(self):
        return self._param

    @property
    def input_size(self):
        return self._input_size

