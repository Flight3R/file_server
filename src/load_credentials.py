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
