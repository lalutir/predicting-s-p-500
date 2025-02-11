import os

def load_api_key():
    keys = {}
    if os.path.exists('personal_key.txt'):
        pass
    else:
        api_key = input('Enter your API key:')
        with open('personal_key.txt', 'w') as file:
            file.write(f'API_KEY={api_key}')
    
    with open('personal_key.txt', 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            keys[key] = value
        return keys

def load_api_key_github_actions():
    return os.getenv("API_KEY")
