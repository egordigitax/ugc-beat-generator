import os
os.system('rm -rf tests/result/*')
os.system('python cli/cli.py -b tests/sources/demo.wav -o tests/result/ -a tests/sources/demo.png --legacy --shade_path tests/sources/Shadow.png -OT 23')