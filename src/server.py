from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from logger import log, logger
from credentials import get_key, get_username_and_password, get_generated_token, save_token_to_file, remove_token_file
import random
import os

app = Flask(__name__)
app.secret_key = get_key('app_key')

credentials = get_username_and_password('credentials')
USERNAME = credentials['USERNAME']
PASSWORD = credentials['PASSWORD']
CONTENT_DIR = 'content'
TOKEN_DIR = 'token'

log(logger.info, 'Server started')


def authenticated_user():
    return session.get('authenticated', False)


@app.route('/')
def index():
    if not authenticated_user():
        user_ip = "->".join(request.access_route)
        log(logger.info, 'Site visited', f'{user_ip=}')
        return redirect(url_for('login'))
    file_list = os.listdir(CONTENT_DIR)
    return render_template('index.html', files=file_list, token=get_generated_token(TOKEN_DIR))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_ip ="->".join(request.access_route)
        if username == USERNAME and password == PASSWORD:
            session['authenticated'] = 'admin'
            log(logger.info, 'Login succeeded', f'{user_ip=}')
            return redirect(url_for('index'))
        else:
            log(logger.warning, 'Login failed', f'{username=}', f'{password=}', f'{user_ip=}')
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html', error=None)


@app.route('/token/login', methods=['POST'])
def login_with_token():
    token = request.form.get('token')
    user_ip ="->".join(request.access_route)

    if token and token == get_generated_token(TOKEN_DIR):
        remove_token_file(TOKEN_DIR, token)
        session['authenticated'] = token
        log(logger.info, 'Login with token succeeded', f'{token=}', f'{user_ip=}')

        return redirect(url_for('index'))

    log(logger.warning, 'Login with token failed', f'{token=}', f'{user_ip=}')
    return render_template('login.html', token_error='Invalid token')


@app.route('/upload', methods=['POST'])
def upload_file():
    auth_id = authenticated_user()
    if not auth_id:
        return redirect(url_for('login'))

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        file.save(os.path.join(CONTENT_DIR, file.filename))
        user_ip ="->".join(request.access_route)
        filename = file.filename
        log(logger.info, 'File uploaded', f'{filename=}', f'{auth_id=}', f'{user_ip=}')
        return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    auth_id = authenticated_user()
    if not auth_id:
        return redirect(url_for('login'))

    user_ip ="->".join(request.access_route)
    log(logger.info, 'File downloaded', f'{filename=}', f'{auth_id=}', f'{user_ip=}')
    return send_from_directory(CONTENT_DIR, filename)


@app.route('/token/generate')
def generate_token():
    auth_id = authenticated_user()
    if auth_id != 'admin':
        return redirect(url_for('login'))

    random_number = random.randint(0, 9999)
    token = f"{random_number:04d}"
    save_token_to_file(TOKEN_DIR, token)

    user_ip ="->".join(request.access_route)
    log(logger.info, 'Token generated', f'{token=}', f'{auth_id=}', f'{user_ip=}')

    return redirect(url_for('index'))


@app.route('/token/remove/<token>')
def remove_token(token):
    auth_id = authenticated_user()
    if auth_id != 'admin':
        return redirect(url_for('login'))

    try:
        remove_token_file(TOKEN_DIR, token)
        user_ip ="->".join(request.access_route)
        log(logger.info, 'Token removed', f'{token=}', f'{auth_id=}', f'{user_ip=}')
    except ValueError:
        pass
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    auth_id = authenticated_user()
    if auth_id:
        user_ip ="->".join(request.access_route)
        log(logger.info, 'Session terminated', f'{auth_id=}', f'{user_ip=}')
        session.pop('authenticated', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
