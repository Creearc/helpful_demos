import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import time

import combine_barcodes_linux as combine_barcodes

ALLOWED_EXTENSIONS = set(['pdf'])
path = 'files'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = path

template = '''
<!doctype html>
    <title>Wildberries pdf to jpg converter</title>
    <h1>Wildberries pdf to jpg converter</h1>
    <h4>
    <p>0_0</p>
    <p>{}</p>
    <p></p>
    </h4>
    <form action="" method=post enctype=multipart/form-data>
      <p>Файлы: <input type=file name=file_1 multiple ></p>
      <p><input type=submit value=Upload></p>
    </form>
'''


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file_1')
        res_files = []
        for file in files:
            tmp_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(tmp_path)
            res_files.append(tmp_path)

        out = combine_barcodes.main(res_files,
                                    'tmp',
                                    'results',
                                    50,
                                    4)
        
        for file in res_files:
            os.remove(file)
            
        if out:
            out = combine_barcodes.zip('results', app.config['UPLOAD_FOLDER'], 'itog_{}'.format(str(time.time()).split('.')[0]))
            for file in os.listdir('results'):
                os.remove('results/{}'.format(file))
            return redirect(url_for('uploaded_file',
                                    filename=out))
        else:
            return template.format('Ошибка! Файл не создан!')
            
    return template.format('')



from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):  
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__ == "__main__":
    folders = [path]
    for folder in folders:
        if not os.path.exists(folder): os.makedirs(folder)
    app.run(host='0.0.0.0', port=56070, debug=True)
