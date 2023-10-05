import os

os.system('ffmpeg -framerate 30 -i output/final/img%04d.png -i tests/sources/shum.mp3 -c:v libx264 -c:a aac -pix_fmt yuv420p -r 30 output.mp4')