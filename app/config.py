from pydantic_settings import BaseSettings, SettingsConfigDict
import os

is_production = False
try:
    is_production = os.environ['ENVIRONMENT'] == 'production'
except KeyError:
    is_production = False

class Settings(BaseSettings):
    username : str
    password : str
    redis_host: str
    redis_port: str
    redis_pwd: str
    kafka_host: str
    github_username: str
    github_token: str


    model_config = None
    if is_production:
        username = os.environ['ENV_USERNAME']
        password = os.environ['ENV_PASSWORD']
        redis_host = os.environ['REDISCLOUD_HOST']
        redis_port = os.environ['REDISCLOUD_PORT']
        redis_pwd = os.environ['REDISCLOUD_PWD']
        kafka_host = os.environ['KAFKA_HOST']
        github_username = os.environ['GITHUB_USERNAME']
        github_token = os.environ['GITHUB_TOKEN']
    else:
        model_config = SettingsConfigDict(env_file='.env')
         
Config = Settings()
