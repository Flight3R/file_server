from flask import Flask, send_from_directory, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    file_list = os.listdir('content')
    return render_template('index.html', files=file_list)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('content', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
