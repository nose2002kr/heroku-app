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
        return dict(sorted(dictionary.items(), key=lambda item: item[1]['bytes'], reverse=True))
    
    @cache(expire=3600)
    async def get_used_language_count(self, username=USERNAME, sort=True):
        logger.debug(f'Getting used language count for {username}')
        repos = await self.__get_repositories(username)
        language_count = defaultdict(lambda: defaultdict(int))
        logger.debug(f'Got repositories for {username}')
        for repo in repos['items']:
            languages = await self.__get_language_stats(repo)
            for language, bytes_of_code in languages.items():
                language_count[language]['bytes'] += bytes_of_code
                if 'biggest_project' not in language_count[language]:
                    language_count[language]['bytes_of_the_biggest_project'] = bytes_of_code
                    language_count[language]['biggest_project'] = repo['name']
                elif language_count[language]['bytes_of_the_biggest_project'] < bytes_of_code:
                    language_count[language]['bytes_of_the_biggest_project'] = bytes_of_code
                    language_count[language]['biggest_project'] = repo['name']


        logger.debug(f'Sortting dictionary: {sort}')
        if sort:
            language_count = self.__sort_item(language_count)
        
        logger.debug(f'Got used language count for {username}')
        return language_count

if __name__ == '__main__':
    from fastapi_cache import FastAPICache
    from fastapi_cache.backends.inmemory import InMemoryBackend
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")

    api = GithubAPI()
    import asyncio
    print(asyncio.run(api.get_used_language_count()))
    