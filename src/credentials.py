import os
import sys
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


def generate_download_token_file(path, filename) -> int:
    random_number = random.randint(0, 999999)
    token = f"{random_number:06d}"
    token_file_path = os.path.join(path, token)
    save_to_file(token_file_path, filename)
    return token


def get_filename_from_download_token_file(filepath) -> str:
    with open(filepath, 'r') as file:
        filename = file.read()
    return filename


def is_download_token_generated_for_file(path, filename):
    tokens = os.listdir(path)
    for token in tokens:
        with open(os.path.join(path, token), 'r') as file:
            if file.read() == filename:
                return True
    return False


def get_generated_token(path):
    tokens = os.listdir(path)
    try:
        return tokens[0]
    except IndexError:
        return None

def get_tokens_for_files_dict(path):
    tokens_for_files_dict = {}
    tokens = os.listdir(path)
    for token in tokens:
        with open(os.path.join(path, token), 'r') as file:
            filename = file.read()
            tokens_for_files_dict[filename] = token
    return tokens_for_files_dict


def save_token_to_file(path, token):
    with open(os.path.join(path, token), 'w'):
        pass


def save_to_file(path, value):
    with open(path, 'w') as file:
        file.write(value)


def is_directory_empty(directory) -> bool:
    log(logger.debug, sys._getframe().f_code.co_name)
    return not any(os.listdir(directory))


def is_file_present(directory, filename) -> bool:
    return os.path.exists(os.path.join(directory, filename))


