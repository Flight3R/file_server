from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import logging
from datetime import timedelta
import random
import sys
import os
from logger import log, logger
from credentials import load_secret, generate_token_file, get_generated_token, get_token_files_dict, save_token_to_file, is_file_token_valid


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)


app = Flask(__name__)

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
app.secret_key = load_secret('APP_KEY')

USERNAME = load_secret('USERNAME')
PASSWORD = load_secret('PASSWORD')
CONTENT_DIR = 'storage/content'
LINKS_DIR = 'storage/links'
STATIC_DIR = 'static'
TOKEN_DIR = 'storage/token'

log(logger.info, 'Server started')


def is_user_authenticated():
    log(logger.debug, sys._getframe().f_code.co_name)
    return session.get('authenticated', False)


def serve_index(**kwargs):
    log(logger.debug, sys._getframe().f_code.co_name)

    file_list = os.listdir(CONTENT_DIR)
    generate_token = get_generated_token(TOKEN_DIR)
    token_files_dict = get_token_files_dict(LINKS_DIR)
    return render_template('index.html', files=file_list, token=generate_token, token_files=token_files_dict, **kwargs)


def is_directory_empty(directory) -> bool:
    log(logger.debug, sys._getframe().f_code.co_name)
    return not any(os.listdir(directory))


def is_file_present(directory, filename) -> bool:
    return os.path.exists(os.path.join(directory, filename))


@app.route('/favicon.ico')
def favicon_request():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index_request():
    log(logger.debug, sys._getframe().f_code.co_name)

    if not is_user_authenticated():
        user_ip = "->".join(request.access_route)
        log(logger.info, 'Site visited', f'{user_ip=}')
        return redirect(url_for('login_request'))
    return serve_index()


@app.route('/login', methods=['GET', 'POST'])
def login_request():
    log(logger.debug, sys._getframe().f_code.co_name)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_ip = "->".join(request.access_route)
        if username == USERNAME and password == PASSWORD:
            session['authenticated'] = 'admin'
            log(logger.info, 'Login succeeded', f'{user_ip=}')
            return redirect(url_for('index_request'))
        else:
            log(logger.warning, 'Login failed', f'{username=}', f'{password=}', f'{user_ip=}')
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html', error=None)


@app.route('/token/login', methods=['POST'])
def login_with_token_request():
    log(logger.debug, sys._getframe().f_code.co_name)

    token = request.form.get('token')
    user_ip = "->".join(request.access_route)

    if token != get_generated_token(TOKEN_DIR):
        log(logger.warning, 'Login with token failed', f'{token=}', f'{user_ip=}')
        return render_template('login.html', token_error='Invalid token')

    os.remove(os.path.join(TOKEN_DIR, token))
    session['authenticated'] = token
    log(logger.info, 'Login with token succeeded', f'{token=}', f'{user_ip=}')
    return redirect(url_for('index_request'))


@app.route('/upload', methods=['POST'])
def upload_file_request():
    log(logger.debug, sys._getframe().f_code.co_name)

    auth_id = is_user_authenticated()
    user_ip = "->".join(request.access_route)
    if not auth_id:
        log(logger.warning, 'Unauthorized upload try', f'{user_ip=}')
        return redirect(url_for('login_request'))

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    filename = file.filename
    if filename == '':
        return redirect(request.url)

    if  is_file_present(CONTENT_DIR, filename):
        return serve_index(error="Filename already in use!")

    file_path = os.path.join(CONTENT_DIR, filename)
    file.save(file_path)
    log(logger.info, 'File uploaded', f'{filename=}', f'{auth_id=}', f'{user_ip=}')
    if auth_id != 'admin':
        token_file_path = os.path.join(LINKS_DIR, filename)
        token = generate_token_file(token_file_path)
        log(logger.info, 'Token for uploaded file generated', f'{filename=}', f'{token=}', f'{auth_id=}', f'{user_ip=}')
    return redirect(url_for('index_request'))


@app.route('/download/<filename>/<token>')
def download_file_token_request(filename, token):
    log(logger.debug, sys._getframe().f_code.co_name)
    user_ip = "->".join(request.access_route)
    file_token_path = os.path.join(LINKS_DIR, filename)
    if not is_file_token_valid(file_token_path, token):
        log(logger.warning, 'Unauthorized download try', f'{user_ip=}')
        return redirect(url_for('index_request'))

    os.remove(file_token_path)
    log(logger.info, 'File downloaded', f'{filename=}', f'{token=}', f'{user_ip=}')
    return send_from_directory(CONTENT_DIR, filename)


@app.route('/token/generate')
def generate_token_request():
    log(logger.debug, sys._getframe().f_code.co_name)

    auth_id = is_user_authenticated()
    user_ip = "->".join(request.access_route)

    if auth_id != 'admin':
        return redirect(url_for('login_request'))

    if is_directory_empty(TOKEN_DIR):
        random_number = random.randint(0, 9999)
        token = f"{random_number:04d}"
        save_token_to_file(TOKEN_DIR, token)
        log(logger.info, 'Token generated', f'{token=}', f'{auth_id=}', f'{user_ip=}')
    else:
        log(logger.error, 'Tried to generate second token', f'{auth_id=}', f'{user_ip=}')

    return redirect(url_for('index_request'))


@app.route('/token/generate/<filename>')
def generate_token_file_request(filename):
    log(logger.debug, sys._getframe().f_code.co_name)

    auth_id = is_user_authenticated()
    user_ip = "->".join(request.access_route)

    if auth_id != 'admin':
        return redirect(url_for('login_request'))

    if not is_file_present(LINKS_DIR, filename):
        token_file_path = os.path.join(LINKS_DIR, filename)
        token = generate_token_file(token_file_path)
        log(logger.info, 'Token for file generated', f'{filename=}', f'{token=}', f'{auth_id=}', f'{user_ip=}')
    else:
        log(logger.error, 'Tried to generate second token for file', f'{filename=}', f'{auth_id=}', f'{user_ip=}')

    return redirect(url_for('index_request'))


@app.route('/token/remove/<token>')
def remove_token_request(token):
    log(logger.debug, sys._getframe().f_code.co_name)

    auth_id = is_user_authenticated()
    user_ip = "->".join(request.access_route)
    if auth_id != 'admin':
        log(logger.warning, 'Tried to remove token', f'{token=}', f'{auth_id=}', f'{user_ip=}')
        return redirect(url_for('login_request'))

    if token.isdigit() and len(token) == 4:
        token_path = os.path.join(TOKEN_DIR, token)
        try:
            os.remove(token_path)
            log(logger.info, 'Token removed', f'{token=}', f'{auth_id=}', f'{user_ip=}')
        except FileNotFoundError:
            pass
    else:
        filename = token
        token_file_path = os.path.join(LINKS_DIR, filename)
        try:
            os.remove(token_file_path)
            log(logger.info, 'Token removed for file', f'{filename=}', f'{auth_id=}', f'{user_ip=}')
        except FileNotFoundError:
            pass

    return redirect(url_for('index_request'))


@app.route('/logout')
def logout_request():
    log(logger.debug, sys._getframe().f_code.co_name)

    auth_id = is_user_authenticated()
    if auth_id:
        user_ip = "->".join(request.access_route)
        log(logger.info, 'Session terminated', f'{auth_id=}', f'{user_ip=}')
        session.pop('authenticated', None)
    return redirect(url_for('login_request'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
