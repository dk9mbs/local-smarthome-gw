import json
import uuid
from flask import Flask
from clientlib import RestApiClient
from config import CONFIG
from core.log import create_logger

logger=create_logger(__name__)

class AppInfo:
    _app=None
    _current_config={}

    @classmethod
    def init(cls,name,config):
        cls._current_config=config
        cls._app=Flask(name)
        cls._app.config['RESTAPI_USER']=config['restapi']['user']
        cls._app.config['RESTAPI_PASSWORD']=config['restapi']['password']
        cls._app.config['RESTAPI_URL']=config['restapi']['url']
        cls._app.config['LOCATION']=config['location']['id']
        cls._app.config['GW_PORT']=5000
        cls._app.config['GW_HOST']="127.0.0.1"

        if 'server' in config:
            if 'port' in config['server']:
                cls._app.config['GW_PORT'] = config['server']['port']
            if 'host' in config['server']:
                cls._app.config['GW_HOST'] = config['server']['host']

        cls._app.secret_key = "MySecretKey1234"

    @classmethod
    def create_restapi_client(cls):
        client=RestApiClient(root_url=AppInfo.get_restapi_url())
        client.login(AppInfo.get_restapi_user(),AppInfo.get_restapi_password())
        return client

    @classmethod
    def set_current_config(cls,section,key,value):
        cls._current_config[section][key]=value

    @classmethod
    def get_current_config(cls, section=None, key=None, default=None, exception=False):
        if section==None:
            return cls._current_config
        else:
            if section in cls._current_config:
                if key in cls._current_config[section]:
                    return cls._current_config[section][key]

            if exception==True:
                raise ConfigNotValid(f"key {key} not found in section {section}")
            else:
                return default

    @classmethod
    def get_server_port(cls):
        return int(cls._app.config['GW_PORT'])

    @classmethod
    def get_server_host(cls):
        return cls._app.config['GW_HOST']

    @classmethod
    def get_restapi_user(cls):
        return cls._app.config['RESTAPI_USER']

    @classmethod
    def get_restapi_password(cls):
        return cls._app.config['RESTAPI_PASSWORD']

    @classmethod
    def get_restapi_url(cls):
        return cls._app.config['RESTAPI_URL']

    @classmethod
    def get_location(cls):
        return cls._app.config['LOCATION']

    @classmethod
    def get_app(cls):
        return cls._app

