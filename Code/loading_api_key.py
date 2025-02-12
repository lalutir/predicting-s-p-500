import os

def load_api_key() -> dict:
    """
    Load the API key from a file or ask the user to input it

    Returns
    -------
    dict
        Dictionary with the API key
    """    
    # Check if the file exists, if not ask the user to input the API key
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

def load_api_key_github_actions() -> str:
    """
    Load the API key from the environment

    Returns
    -------
    str
        API key
    """    
    
    return os.getenv("API_KEY")
