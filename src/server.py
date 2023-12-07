from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from logger import logger
from credentials import get_key, get_username_and_password, get_generated_tokens, save_token_to_file, remove_token_file
import random
import os

app = Flask(__name__)
app.secret_key = get_key('app_key')

credentials = get_username_and_password('credentials')
USERNAME = credentials['USERNAME']
PASSWORD = credentials['PASSWORD']
CONTENT_DIR = 'content'
TOKEN_DIR = 'tokens'

logger.info('Server started')


def authenticated_user():
    return session.get('authenticated', False)


@app.route('/')
def index():
    if not authenticated_user():
        user_ip = "->".join(request.access_route)
        logger.info(f'Site visited by {user_ip}')
        return redirect(url_for('login'))
    file_list = os.listdir(CONTENT_DIR)
    return render_template('index.html', files=file_list, generated_tokens=get_generated_tokens(TOKEN_DIR))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_ip ="->".join(request.access_route)
        if username == USERNAME and password == PASSWORD:
            session['authenticated'] = 'admin'
            logger.info(f'Login succeeded by {user_ip}')
            return redirect(url_for('index'))
        else:
            logger.warning(f'Login with {username}:{password} failed by {user_ip}')
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html', error=None)


@app.route('/token/login', methods=['POST'])
def login_with_token():
    token_to_use = request.form.get('token')
    user_ip ="->".join(request.access_route)

    if token_to_use and token_to_use in get_generated_tokens(TOKEN_DIR):
        remove_token_file(TOKEN_DIR, token_to_use)
        session['authenticated'] = token_to_use
        logger.info(f'Login with token {token_to_use} succeeded by {user_ip}')

        return redirect(url_for('index'))

    logger.warning(f'Login with token {token_to_use} failed by {user_ip}')
    return render_template('login.html', token_error='Invalid token')


@app.route('/upload', methods=['POST'])
def upload_file():
    if not authenticated_user():
        return redirect(url_for('login'))

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        file.save(os.path.join(CONTENT_DIR, file.filename))
        user_ip ="->".join(request.access_route)
        logger.info(f'File {file.filename} uploaded by {authenticated_user()} ({user_ip})')
        return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    if not authenticated_user():
        return redirect(url_for('login'))

    user_ip ="->".join(request.access_route)
    logger.info(f'File {filename} downloaded by {authenticated_user()} ({user_ip})')
    return send_from_directory(CONTENT_DIR, filename)


@app.route('/token/generate')
def generate_token():
    if authenticated_user() != 'admin':
        return redirect(url_for('login'))

    random_number = random.randint(0, 9999)
    token = f"{random_number:04d}"
    save_token_to_file(TOKEN_DIR, token)

    user_ip ="->".join(request.access_route)
    logger.info(f'Token {token} generated by {authenticated_user()} ({user_ip})')

    return redirect(url_for('index'))


@app.route('/token/remove/<token_to_remove>')
def remove_token(token_to_remove):
    if authenticated_user() != 'admin':
        return redirect(url_for('login'))

    try:
        remove_token_file(TOKEN_DIR, token_to_remove)
        user_ip ="->".join(request.access_route)
        logger.info(f'Token {token_to_remove} removed by {authenticated_user()} ({user_ip})')
    except ValueError:
        pass
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    user_ip ="->".join(request.access_route)
    logger.info(f'Session terminated by {authenticated_user()} ({user_ip})')
    session.pop('authenticated', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
