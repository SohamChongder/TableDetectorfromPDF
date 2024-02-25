from flask import *
from flask_wtf import FlaskForm
from pdf2image import convert_from_path
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from script import extract_table_from_image
from markupsafe import Markup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER']='output'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")




@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        ext=file.filename.split('.')[-1]
        if(ext=='pdf'):
            print("Es ist PDF")
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
            pages = convert_from_path(os.path.join(app.config['UPLOAD_FOLDER'],file.filename), 500)
            for page in pages:
                page.save("converted_img.png", "PNG")
                extract_table_from_image("converted_img.png",os.path.join(current_app.root_path, app.config['OUTPUT_FOLDER'],"output.csv"))
                flash("Uploaded successfully")
                return render_template('index.html', form=form, filename="output.csv")
        else:
            print("Not Good den es ist "+str(file.filename))
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
            extract_table_from_image(os.path.join(app.config['UPLOAD_FOLDER'],file.filename),os.path.join(current_app.root_path, app.config['OUTPUT_FOLDER'],"output.csv"))
            flash("Uploaded successfully")
            return render_template('index.html', form=form, filename="output.csv")
    return render_template('index.html', form=form)

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    # Appending app path to upload folder path within app root folder
    uploads = os.path.join(current_app.root_path, app.config['OUTPUT_FOLDER'])
    return send_from_directory(uploads, filename)

if __name__ == '__main__':
    app.run(debug=True)
