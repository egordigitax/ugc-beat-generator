import os

from settings import FINAL_RENDER, SCENE_OUTPUT, OVERLAY_OUTPUT, USER_OUTPUT

print('Removing old frames...')
os.system(f'rm {FINAL_RENDER}/*')
os.system(f'rm {SCENE_OUTPUT}/*')
os.system(f'rm {OVERLAY_OUTPUT}/*')
os.system(f'rm {USER_OUTPUT}/*')
print('Testing new generator...')
os.system(f'python cli.py -b tests/sources/shum.mp3 -o {FINAL_RENDER} -a tests/sources/dav.jpg --shade_path tests/sources/Shadow.png -t 1 -ot 1 -ut 1 -un LOUISDIOO -tn Шумодав --overlay_opacity 0.8')
print('Testing legacy generator...')
# os.system(f'python cli.py -b tests/sources/shum.mp3 -o {FINAL_RENDER} -a tests/sources/dav.jpg --shade_path tests/sources/Shadow.png -t 1 -ot 1 -ut 1 -un Yardie -tn SportsClub --legacy')
