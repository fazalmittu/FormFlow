from flask import Flask, request, redirect, url_for, render_template, flash, jsonify, session
import boto3
import os
from dotenv import load_dotenv
from critic.gptv import critique_video
import subprocess
import json
import pprint
from critic import critic
from critic.summary import display_initial_analysis

from openpose_overlay.overlay import generate_video

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB
app.secret_key = 'supersecretkey'  # Secret key for signing cookies

# AWS S3 configuration
load_dotenv()
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION')
EXTERNAL_S3_BUCKET = os.environ.get('EXTERNAL_S3_BUCKET')
print(EXTERNAL_S3_BUCKET)
# Initialize boto3 client
s3 = boto3.client(
    's3', 
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run-critic')
def run_critic():
    print("made it to run critic")
    critique_result = session.get('critique_result', {})
    overall_critique = critique_result.get('overall_critique', '')
    critic.main(overall_critique)


@app.route('/feedback')
def feedback():
    print("CAROUSEL FOUND")
    flash("MADE IT TO CAROUSEL")
    critique_result = session.get('critique_result')  # Retrieve from session
    print(critique_result)
    if critique_result:
        student_key_frames = critique_result.get("student_key_frames", [])
        key_frame_paths = [f'frame_{str(int(frame))}.jpg' for frame in student_key_frames]
    else:
        key_frame_paths = []
    return render_template('carousel.html', key_frame_paths=key_frame_paths)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        generate_video(filepath)
        print("ABOUT TO CRITIQUE")
        critique_result = critique_video("uploads/output_video.mp4")
        print(critique_result)
        session['critique_result'] = critique_result  # Store in session
        return redirect(url_for('summary'))  # Redirect to the summary page
    else:
        flash('Invalid file type')
        return redirect(url_for('index'))


@app.route('/summary')
def summary():
    video_path = session.get('video_path', 'default_video.mp4')  # Ensure you set this in your upload or processing route
    return display_initial_analysis(video_path)


if __name__ == '__main__':
    app.run(debug=True)
