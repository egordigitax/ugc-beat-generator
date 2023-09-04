from cli.engine.blender import BlenderEngine

engine = BlenderEngine('sdk/blender/blender-3.6.2-linux-x64/blender')
engine.render('tests/sources/project.blend', 'tests/', 1)
