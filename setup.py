import os.path
from distutils.core import setup

def get_dependencies(file_name=None):
    if file_name is None:
        file_name = os.path.join(os.path.dirname(__file__),'requirements.txt')

    out = []
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip()
            if line[0:2] == '-r':
                out += get_dependencies(os.path.join(os.path.dirname(file_name), line[3:]))
            elif line[0:1] != '#':
                out.append(line)
    return out


setup(
    name='sparrow',
    version='0.0.1',
    package_data={'sparrow': ['*'], },
    author='Wikia',
    description='Performance monitoring tool',
    install_requires=get_dependencies()
)
