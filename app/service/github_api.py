import requests
from collections import defaultdict
from config import Config

USERNAME = Config.github_username
TOKEN = Config.github_token

class GithubAPI:
    def __get_repositories(self, username):
        url = f'https://api.github.com/search/repositories?q=user:{username}'
        headers = {'Authorization': f'token {TOKEN}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()

    def __get_language_stats(self, repo):
        url = repo['languages_url']
        headers = {'Authorization': f'token {TOKEN}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def __sort_item(self, dictionary):
        return dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))
    
    def get_used_language_count(self, username, sort=True):
        repos = self.__get_repositories(username)
        language_count = defaultdict(int)

        for repo in repos['items']:
            languages = self.__get_language_stats(repo)
            for language, bytes_of_code in languages.items():
                language_count[language] += bytes_of_code

        if sort:
            language_count = self.__sort_item(language_count)
        return language_count
