import requests
import re
import docker
from docker.errors import APIError

# Docker login (if necessary, especially for private repositories)
client = docker.from_env()


# client.login(username='your_username', password='your_password')  # Uncomment if login is needed

def list_repository_tags(repository, pattern):
    """
    List all tags from a Docker repository that match a given pattern.

    Args:
        repository (str): Docker repository in the format 'username/repo'
        pattern (str): Regex pattern to match tags

    Returns:
        list: A list of matching tags
    """
    tags = []
    url = f"https://registry.hub.docker.com/v2/repositories/{repository}/tags"

    while url:
        response = requests.get(url)
        if response.status_code == 200:
            json_response = response.json()
            tags.extend([result['name'] for result in json_response['results'] if re.match(pattern, result['name'])])
            url = json_response['next']  # Continue with the next page of tags
        else:
            raise Exception(f"Failed to fetch tags from Docker Hub: {response.status_code}")

    return tags


def pull_images(repository, tags):
    """
    Pull images based on a list of tags.

    Args:
        repository (str): Docker repository in the format 'username/repo'
        tags (list): List of tags to pull
    """
    for tag in tags:
        try:
            image = client.images.pull(f"{repository}:{tag}")
            print(f"Successfully pulled {image.tags}")
        except APIError as e:
            print(f"Failed to pull {repository}:{tag}: {e}")


# Example usage
repository = 'library/nginx'  # Public repo example
pattern = r'^1\.19.*'  # Regex to match specific versions, e.g., versions starting with 1.19
tags = list_repository_tags(repository, pattern)
pull_images(repository, tags)
