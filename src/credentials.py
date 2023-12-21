import os
from logger import logger, log


def load_secret(secret_key):
    log(logger.info, "Loading secret", f"{secret_key=}")
    secret_value = os.environ.get(secret_key)
    if secret_value is None:
        log(logger.critical, "Loading secret failed", f"{secret_key=}")
        raise ValueError
    log(logger.debug, "Secret loaded", f"{secret_value=}")
    return secret_value


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
    os.remove(os.path.join(path, token))
