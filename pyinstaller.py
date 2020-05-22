import os
from shutil import rmtree
from time import sleep
import PyInstaller.__main__


package_name = 'SocialFabric'

# Used to copy example directories
def recurse_add_data(target):
    all_path = []
    for path, dirs, files in os.walk(target):
      for file in files:
          if not file.startswith('.'):
            all_path.append('--add-data=' + path + os.sep + file + ':' + path)
    return all_path

# Remove previous built (including setup built)
try:
    rmtree('build')
except:
    pass
try:
    rmtree('dist')
except:
    pass
try:
    os.remove(package_name + '.spec')
except:
    pass

sleep(0.2)

# Build
PyInstaller.__main__.run(
    ['--name=%s' % package_name,
     '--onefile',
     #'--onedir',
     '--add-data=social_fabric/templates/*.html:social_fabric/templates',
     '--add-data=social_fabric/static/js/*.js:social_fabric/static/js',
     '--add-data=social_fabric/static/css/*.css:social_fabric/static/css']
    + recurse_add_data('social_fabric/example-network')
    + recurse_add_data('social_fabric/example-attach')
    + ['--add-binary=social_fabric/bin/*:social_fabric/bin',
       os.path.join('social_fabric', '__main__.py')])
