import requests
from collections import defaultdict
from app.config import Config
from fastapi_cache.decorator import cache
from loguru import logger

from app.core.singleton import Singleton

USERNAME = Config.github_username
TOKEN = Config.github_token

class GithubAPI(metaclass=Singleton):
    async def __get_repositories(self, username=USERNAME, token=TOKEN):
        logger.debug(f'Getting repositories for {username}')
        url = f'https://api.github.com/search/repositories?q=user:{username}'
        headers = {'Authorization': f'token {token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        logger.debug(f'Got repositories for {username}')
        return response.json()

    async def __get_language_stats(self, repo, token=TOKEN):
        logger.debug(f'Getting language stats for {repo["name"]}')
        url = repo['languages_url']
        headers = {'Authorization': f'token {token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.debug(f'Got language stats for {repo["name"]}')
        return response.json()

    def __sort_item(self, dictionary):
        return dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))
    
    @cache(expire=3600)
    async def get_used_language_count(self, username=USERNAME, sort=True):
        logger.debug(f'Getting used language count for {username}')
        repos = await self.__get_repositories(username)
        language_count = defaultdict(int)
        logger.debug(f'Got repositories for {username}')
        for repo in repos['items']:
            languages = await self.__get_language_stats(repo)
            for language, bytes_of_code in languages.items():
                language_count[language] += bytes_of_code

        logger.debug(f'Sortting dictionary: {sort}')
        if sort:
            language_count = self.__sort_item(language_count)
        
        logger.debug(f'Got used language count for {username}')
        return language_count
