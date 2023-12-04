from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from logger import logger
from load_credentials import get_key, get_username_and_password
import os

app = Flask(__name__)
app.secret_key = get_key('app_key')

credentials = get_username_and_password('credentials')
USERNAME = credentials['USERNAME']
PASSWORD = credentials['PASSWORD']

CONTENT_FOLDER = 'content'

def is_user_authenticated():
    return session.get('authenticated', False)

@app.route('/')
def index():
    if not is_user_authenticated():
        return redirect(url_for('login'))

    file_list = os.listdir(CONTENT_FOLDER)
    return render_template('index.html', files=file_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == USERNAME and password == PASSWORD:
            session['authenticated'] = True
            user_ip = request.remote_addr
            logger.info(f'Login successfull from {user_ip}')
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html', error=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if not is_user_authenticated():
        return redirect(url_for('login'))

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        file.save(os.path.join(CONTENT_FOLDER, file.filename))
        user_ip = request.remote_addr
        logger.info(f'File "{file.filename}" uploaded by {user_ip}.')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    if not is_user_authenticated():
        return redirect(url_for('login'))

    user_ip = request.remote_addr
    logger.info(f'File "{filename}" downloaded by {user_ip}.')
    return send_from_directory(CONTENT_FOLDER, filename)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
