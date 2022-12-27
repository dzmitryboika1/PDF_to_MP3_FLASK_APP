import os

from dotenv import load_dotenv
from flask import Flask, send_from_directory, render_template, request, redirect, url_for, flash, session, \
    after_this_request
from flask_bootstrap import Bootstrap
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect, CSRFError

from converter import pdf_to_mp3


app = Flask(__name__)
csrf = CSRFProtect(app)
bootstrap = Bootstrap(app)
dropzone = Dropzone(app)

app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY'),
    UPLOAD_FOLDER='uploads', DOWNLOAD_FOLDER='downloads',
    DROPZONE_MAX_FILE_SIZE=3,  # 3Mb
    DROPZONE_MAX_FILES=1,
    DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE='.pdf',
    DROPZONE_DEFAULT_MESSAGE='Drop your PDF file here to upload (max size up to 3 MB)',
    DROPZONE_UPLOAD_MULTIPLE=False, DROPZONE_ENABLE_CSRF=True,
)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['DROPZONE_ALLOWED_FILE_TYPE']


@app.route('/')
def home():
    return render_template("index.html", pdf_converted=request.args.get('pdf_converted'))


@app.route('/upload-pdf', methods=["POST", "GET"])
def upload_pdf():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        pdf_file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if pdf_file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if pdf_file and allowed_file(pdf_file.filename):
            filename = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['pdf_file_name'] = filename
            return redirect(url_for('convert'))

        return redirect(url_for('home'))


@app.route('/convert')
def convert():
    pdf_file_name = session.get('pdf_file_name', None)
    if pdf_file_name:
        pdf_file_path = f"{app.config['UPLOAD_FOLDER']}/{pdf_file_name}"
        mp3_file_name = pdf_to_mp3(pdf_file_path, app.config['DOWNLOAD_FOLDER'])
        if mp3_file_name:
            session['mp3_file_name'] = mp3_file_name
            return redirect(url_for('home', pdf_converted=True))
        flash('Oops, something went wrong. Please, try again!', 'error')
        return redirect(url_for('home'))

    flash('Please, upload file!', 'error')
    return redirect(url_for('home'))


@app.route('/download')
def download():

    @after_this_request
    def clear_dirs(response):
        os.remove(f"{app.config['UPLOAD_FOLDER']}/{session['pdf_file_name']}")
        os.remove(f"{app.config['DOWNLOAD_FOLDER']}/{session['mp3_file_name']}")
        return response

    return send_from_directory(directory=app.config['DOWNLOAD_FOLDER'], path=session['mp3_file_name'],
                               as_attachment=True)


# handle CSRF error
@app.errorhandler(CSRFError)
def csrf_error(e):
    return e.description, 400


if __name__ == '__main__':
    load_dotenv()
    app.run()
