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

arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

for i in range(0, 150):
    print(arr[i % len(arr)])