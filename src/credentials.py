import os


def get_key(file_path):
    """
    :raises FileNotFoundError
    """
    with open(file_path, 'r') as api_key_file:
        api_key = api_key_file.read().strip()
    return api_key


def get_username_and_password(file_path):
    """
    :raises FileNotFoundError
    """
    with open(file_path, 'r') as credentials_file:
        credentials = {}
        for key, line in zip(['USERNAME', 'PASSWORD'], credentials_file):
            credentials[key] = line.strip()
    return credentials


def get_generated_token(path):
    tokens = os.listdir(path)
    try:
        return tokens[0]
    except IndexError:
        return None


def save_token_to_file(path, token):
    with open(os.path.join(path, token), 'w'):
        pass


def remove_token_file(path, token):
    """
    :raises FileNotFoundError
    """
    os.remove(os.path.join(path, token))