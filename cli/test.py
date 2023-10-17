import os

from settings import FINAL_RENDER, SCENE_OUTPUT, OVERLAY_OUTPUT, USER_OUTPUT

print('Removing old frames...')
os.system(f'rm {FINAL_RENDER}/*')
os.system(f'rm {SCENE_OUTPUT}/*')
os.system(f'rm {OVERLAY_OUTPUT}/*')
os.system(f'rm {USER_OUTPUT}/*')
print('Testing new generator...')
os.system(f'python3 cli.py -m blender -b tests/sources/demo.wav -o {FINAL_RENDER} -a tests/sources/demo.png -t 1 -ot 1 -ut 1 -un LOUISDIOO -tn Шумодав --overlay_opacity 0.8 --verbose')
print('Testing legacy generator...')
os.system(f'python3 cli.py -m classic -b tests/sources/demo.wav -o {FINAL_RENDER} -a tests/sources/dav.jpg -t 1 -ot 1 -ut 1 -un Yardie -tn SportsClub --verbose')
