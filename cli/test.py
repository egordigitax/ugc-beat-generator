# import os
#
# from services.engine.blender import BlenderEngine
#
# print('Cleaning results folder...')
# os.system('rm tests/result/*')
#
# print('Testing Blender render engine...')
# engine = BlenderEngine('sdk/blender/blender-3.6.2-linux-x64/blender')
# engine.render('tests/sources/project.blend', 'tests/', 1)
# print('Blender engine is fine.')
#
# print('Testing UGC application legacy mode...')
# os.system('.venv/bin/python3 cli.py -b tests/sources/demo.wav -a tests/sources/demo.png -o tests/result/ --shade_path tests/sources/Shadow.png --legacy --verbose')
import os
from PIL import Image

path = 'sources/.output/user'

for file in [folder for folder in os.listdir(path) if folder.endswith('.png')]:
    print(f'resizing {file}')
    image = Image.open(path+'/'+file)
    new_image = image.resize((720, 1280))
    print(f'resized.')
    new_image.save(path+'/'+file)
