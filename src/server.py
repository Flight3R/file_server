from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import logging
from datetime import timedelta
import random
import os
import sys
sys.path.append('apptools/src')
from apptools.src.logger import log, logger
from apptools.src.secrets import load_secret, generate_download_token_file, get_filename_from_download_token_file, is_download_token_generated_for_file, get_generated_token, get_tokens_for_files_dict, save_token_to_file, is_directory_empty, is_file_present


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
os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(LINKS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TOKEN_DIR, exist_ok=True)


log(logger.info, 'Server started')


def is_user_authenticated():
    log(logger.debug, sys._getframe().f_code.co_name)
    return session.get('authenticated', False)


def serve_index(**kwargs):
    log(logger.debug, sys._getframe().f_code.co_name)

    file_list = os.listdir(CONTENT_DIR)
    generate_token = get_generated_token(TOKEN_DIR)
    download_tokens_for_files_dict = get_tokens_for_files_dict(LINKS_DIR)
    return render_template('index.html', files=file_list, token=generate_token, tokens_for_files=download_tokens_for_files_dict, **kwargs)


@app.route('/favicon.ico')
def favicon_request():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',mimetype='image/x-icon')


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
            return render_template('login.html', error='Invalid credentials!')

    return render_template('login.html', error=None)


@app.route('/token/login', methods=['POST'])
def login_with_token_request():
    log(logger.debug, sys._getframe().f_code.co_name)

    token = request.form.get('token')
    user_ip = "->".join(request.access_route)

    if token != get_generated_token(TOKEN_DIR):
        log(logger.warning, 'Login with token failed', f'{token=}', f'{user_ip=}')
        return render_template('login.html', token_error='Invalid login token!')

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


    if is_file_present(CONTENT_DIR, filename):
        return serve_index(error="Filename already in use!")

    file_path = os.path.join(CONTENT_DIR, filename)
    file.save(file_path)
    log(logger.info, 'File uploaded', f'{filename=}', f'{auth_id=}', f'{user_ip=}')
    if auth_id != 'admin':
        token = generate_download_token_file(LINKS_DIR, filename)
        log(logger.info, 'Token for uploaded file generated', f'{filename=}', f'{token=}', f'{auth_id=}', f'{user_ip=}')
    return redirect(url_for('index_request'))


@app.route('/download/<token>')
def download_file_request(token):
    log(logger.debug, sys._getframe().f_code.co_name)
    user_ip = "->".join(request.access_route)
    download_file_token_path = os.path.join(LINKS_DIR, token)
    if not is_file_present(LINKS_DIR, token):
        log(logger.warning, 'Unauthorized download try', f'{token=}', f'{user_ip=}')
        return redirect(url_for('index_request'))
    filename = get_filename_from_download_token_file(download_file_token_path)
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
        log(logger.info, 'Login token generated', f'{token=}', f'{auth_id=}', f'{user_ip=}')
    else:
        log(logger.error, 'Tried to generate second login token', f'{auth_id=}', f'{user_ip=}')

    return redirect(url_for('index_request'))


@app.route('/token/generate/<filename>')
def generate_token_file_request(filename):
    log(logger.debug, sys._getframe().f_code.co_name)

    auth_id = is_user_authenticated()
    user_ip = "->".join(request.access_route)

    if auth_id != 'admin':
        return redirect(url_for('login_request'))

    if not is_download_token_generated_for_file(LINKS_DIR, filename):
        token = generate_download_token_file(LINKS_DIR, filename)
        log(logger.info, 'Download token for file generated', f'{filename=}', f'{token=}', f'{auth_id=}', f'{user_ip=}')
    else:
        log(logger.error, 'Tried to generate second download token for file', f'{filename=}', f'{auth_id=}', f'{user_ip=}')

    return redirect(url_for('index_request'))


@app.route('/token/remove/<token>')
def remove_token_request(token):
    log(logger.debug, sys._getframe().f_code.co_name)

    auth_id = is_user_authenticated()
    user_ip = "->".join(request.access_route)
    if not auth_id:
        log(logger.warning, 'Unauthorized login token removal try', f'{token=}', f'{user_ip=}')
        return redirect(url_for('login_request'))

    if token.isdigit() and len(token) == 4:
        token_path = os.path.join(TOKEN_DIR, token)
        try:
            os.remove(token_path)
            log(logger.info, 'Login token removed', f'{token=}', f'{auth_id=}', f'{user_ip=}')
        except FileNotFoundError:
            pass
    else:
        token_file_path = os.path.join(LINKS_DIR, token)
        try:
            filename = get_filename_from_download_token_file(token_file_path)
            os.remove(token_file_path)
            log(logger.info, 'Download token for file removed', f'{filename=}', f'{token=}', f'{auth_id=}', f'{user_ip=}')
        except FileNotFoundError:
            log(logger.error, 'Tried to remove non existing download token for file', f'{token=}', f'{auth_id=}', f'{user_ip=}')

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
