import os
import random
from logger import logger, log

def load_secret(secret_key):
    log(logger.info, "Loading secret", f"{secret_key=}")
    secret_value = os.environ.get(secret_key)
    if secret_value is None:
        log(logger.critical, "Loading secret failed", f"{secret_key=}")
        raise ValueError
    log(logger.debug, "Secret loaded", f"{secret_value=}")
    return secret_value


def generate_token_file(path):
    random_number = random.randint(0, 9999)
    token = f"{random_number:04d}"
    save_file_token_to_file(path, token)


def get_generated_token(path):
    tokens = os.listdir(path)
    try:
        return tokens[0]
    except IndexError:
        return None

def get_token_files_dict(path):
    token_files_dict = {}
    files = os.listdir(path)
    for filename in files:
        with open(os.path.join(path, filename), 'r') as file:
            token = file.read()
            token_files_dict[filename] = token
    return token_files_dict


def save_token_to_file(path, token):
    with open(os.path.join(path, token), 'w'):
        pass


def save_file_token_to_file(path, token):
    with open(path, 'w') as file:
        file.write(token)


def is_file_token_valid(path, token) -> bool:
    try:
        with open(path, 'r') as file:
            file_content = file.read()
            if file_content == token:
                return True
            else:
                return False
    except FileNotFoundError:
        return False
