from flask import Flask, request, render_template, send_file
import uuid

import service
import subprocess
import os
from pathlib import Path


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads/"
app.config['TEMP_FOLDER'] = "temp/"


assets =  { 
            "beat_name": "assets/Druk Wide Cyr Heavy.otf",
            "author_name": "assets/Golos-Text_Regular.ttf",
            "shade": "assets/Shadow.png"
        }

@app.route("/")
def health():
    return "ok", 200

def clean_folder(folder_path):
    subprocess.check_output("rm -rf {}".format(folder_path), shell=True, text=True)


def create_folder(folder_path):
    Path(folder_path).mkdir(parents=True, exist_ok=True)



@app.route("/generate", methods=['GET', 'POST'])
def generate():
    request_id = str(uuid.uuid4().hex[:10])
    
    if request.method == "POST":
        if not all(ele in request.files for ele in ["beat_file", "cover_file"]):
            return "not enough mana", 500

        beat_name = request.form["beat_name"]
        author_name = request.form["author_name"]

        beat_file = request.files["beat_file"]
        cover_file = request.files["cover_file"]

        smooth = request.form["smooth"]

        base_uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], request_id)
        create_folder(base_uploaded_path)

        temp_path = os.path.join(app.config['TEMP_FOLDER'], request_id)
        create_folder(temp_path)




        uploaded_beat_file_path = os.path.join(base_uploaded_path, beat_file.filename)
        uploaded_cover_file_path = os.path.join(base_uploaded_path, cover_file.filename)

        beat_file.save(uploaded_beat_file_path)
        cover_file.save(uploaded_cover_file_path)

        service.process_track(
                float(smooth),
                temp_path,
                uploaded_beat_file_path,
                uploaded_cover_file_path,
                beat_name,
                author_name,
                assets,
                dbg=False,
                output_file="generated/{}.mp4".format(request_id)
            )

        return send_file("generated/{}.mp4".format(request_id),as_attachment=True)
    else:
        return render_template("upload.html")

@app.route("/test_download")
def test_download():
    return send_file("generated/{}.mp4".format("62816eb947"), as_attachment=True)


@app.route("/test")
def test():
    

    service.process_track(
        "demo.wav",
        "demo.png",
        "Demo Beat",
        "Demo Author",
        assets,
        dbg=False,
        output_file="out_s.mp4"
    )

    return "ok"


