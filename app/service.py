# %matplotlib inline

import librosa
from scipy.ndimage.filters import gaussian_filter
import matplotlib
import numpy as np
import subprocess
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.signal import hilbert, chirp
from PIL import Image, ImageFilter
import math
# from IPython.display import Video

from joblib import Parallel, delayed
from scipy import interpolate
from PIL import Image, ImageFont, ImageDraw

# 576x1024
def process_track(smooth, temp_path, song_path, image_path, beat_name, author_name, asset_path, output_file, framerate = 30, size_w = 720, size_h = 1280, size_a = 400, dbg = True):
    print("Loading song at {}".format(song_path))
    y, sr = librosa.load(song_path)

    print("Generating percussive")

    y_percussive = librosa.effects.percussive(y)
        

    print("Starting postprocessing")
    
    y_perc = (y_percussive - np.min(y_percussive)) / (np.max(y_percussive) - np.min(y_percussive))


    print("Starting hilbert")

    y_perc = np.abs(hilbert(y_perc))


    print("Starting gauss smoothing")

    kernel_size = int(sr/smooth)
    kernel = np.ones(kernel_size) / kernel_size

    kernel_offset = int(kernel_size / 2)
    y_perc = np.concatenate((y_perc[0:kernel_offset], y_perc, y_perc[-kernel_offset:-1]))

    y_perc = np.convolve(y_perc, kernel, mode='valid')

    y_perc = (y_perc - np.min(y_perc)) / (np.max(y_perc) - np.min(y_perc))


    # print("Starting hax")
    #
    # y_perc[0:2000] = y_perc[2000:4000]
    # y_perc[-2001:-1] = y_perc[-4000:-2000]
    #

    print("Loading images")

    
    original_image = Image.open(image_path)
    original_image = original_image.resize((size_a, size_a))
    original_image.putalpha(255)
    

    blurred_image = Image.open(image_path)
    blurred_image.putalpha(255)
    

    blurred_image = blurred_image.filter(ImageFilter.GaussianBlur(10))

    blurred_image = blurred_image.resize((size_h, size_h))
    
    
    shade_image = Image.open(asset_path["shade"])
    
    

    
    def clean_frames():
        subprocess.check_output("rm -rf {}/temp.mp4".format(temp_path), shell=True, text=True)
        subprocess.check_output("rm -rf {}/frames/".format(temp_path), shell=True, text=True)

    def init_frames():
        Path("{}/frames".format(temp_path)).mkdir(parents=True, exist_ok=True)

    def create_save_frame(number, maxNumbers, intensity = 1.0):
        reds = np.zeros([256, 256, 3], dtype=np.float32)
        reds[0:int(255 * intensity), :, 0] = 1.0



        img = Image.fromarray((reds * 255).astype(np.uint8))



        img.save('{}/frames/img{}.png'.format(temp_path, str(number).zfill(maxNumbers)))




    def assemble_video():        
        subprocess.call("ffmpeg -y -framerate {} -pattern_type glob -i '{}/frames/*.png' -c:v libx264 -b:v 4108k -pix_fmt yuv420p {}/temp.mp4".format(framerate, temp_path, temp_path), shell=True, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


    def attach_audio():
        subprocess.call("ffmpeg -y -i {}/temp.mp4 -i {} -map 0:v -map 1:a -c:v copy -shortest {}".format(temp_path, song_path, output_file), shell=True, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        
    def add_corners(im, rad):
        circle = Image.new('L', (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
        alpha = Image.new('L', im.size, 255)
        w, h = im.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        im.putalpha(alpha)
        return im
    
    def add_text(im_p, text, font_path, font_size, color, offset, max_len):
        
        font = ImageFont.truetype(font_path,font_size)
        
        txt = Image.new('RGBA', im_p.size, (255,255,255,0))


        
        draw = ImageDraw.Draw(im_p)
        txt_d = ImageDraw.Draw(txt)
        
        short_text = ""
        
        if len(text) > max_len:
            short_text = text[0:max_len]
            short_text += "..."
        else:
            short_text = text
        

        txt_d.multiline_text(offset, short_text, fill=color, font=font, anchor="mm", spacing=0, align="center")
        

#         txt_d.text(offset,text,anchor='mm',fill= color,font=font)

        im_p = Image.alpha_composite(im_p, txt)    

        return im_p

        
        
    def create_save_frame_img_proto(intensity, image, blurred):
#         reds = np.zeros([size_h, size_w, 3], dtype=np.float32)
        reds = np.zeros([size_h, size_w, 4], dtype=np.float32)
        
        img = Image.fromarray((reds * 255).astype(np.uint8), "RGBA")

        def new_size():
            return int((1.0 - intensity) * size_h + (intensity) * size_h * 2)
        def new_offset(size):
            return int((1.0 - intensity) * (size_w - size_h)/2 + (intensity) * (size_w - size)/2)


        blurred_resized = blurred.resize((new_size(), new_size()))


        img.paste(blurred_resized, (new_offset(size_h * 2), 0))


        img = Image.alpha_composite(img, shade_image)
        

        rounded = add_corners(image, 40)
        img.paste(rounded, (160, 246), rounded)
        

        img = add_text(img, beat_name, asset_path["beat_name"], 25, (255, 255, 255, 255), (size_w/2, 50 + 400 + 246 + 11), 20)
        img = add_text(img, author_name, asset_path["author_name"], 22, (255, 255, 255, int(0.6 * 255)), (size_w/2, 11 + 50 + 400 + 246 + 12 + 16 + 11), 20)
        

        return img


    

    def create_save_frame_img(number, maxNumbers, intensity, image, blurred):
        new_img = create_save_frame_img_proto(intensity, image, blurred)
        new_img.save('{}/frames/img{}.png'.format(temp_path, str(number).zfill(maxNumbers)))

    def process2(i):

        frame_to_time = float(i) / float(framerate)
        audio_time_sample = int(frame_to_time * sr)


        if audio_time_sample < len(y_percussive):
            intensity = y_perc[audio_time_sample]

            create_save_frame_img(i, max_numbers, intensity, original_image, blurred_image)
    
    
    if dbg:
        display(create_save_frame_img_proto(0.0, original_image, blurred_image))
        return
    
    print("Cleaning old frames")

    clean_frames()

    print("Initing frames directory")

    init_frames()



    duration = math.ceil(librosa.get_duration(y=y))
    


    total_frames = duration * framerate


    max_numbers =  int(math.log10(total_frames))+1

    print("Generation")

    
    Parallel(n_jobs=8, verbose=total_frames)(delayed(process2)(i) for i in range (total_frames))
            
    print("Starting assembling")
    
    assemble_video()

    print("Attaching audio")

    attach_audio()

    clean_frames()

