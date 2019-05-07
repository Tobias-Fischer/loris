import distutils.command.build
import distutils.core
import os
import re
import setuptools
import shutil
import sys
dirname = os.path.dirname(os.path.realpath(__file__))

def copy_and_resolve(filename, target_directory):
    """
    copy_and_resolve operates on C++ files.
    It copies 'filename' to the target directory,
    as well as every included file (recursively).
    """
    directory, name = os.path.split(filename)
    children = []
    with open(os.path.join(target_directory, name), 'w') as output:
        with open(filename, 'r') as input:
            for line in input:
                match = re.match(r'^#include "(.+)"$', str(line))
                if match is None:
                    output.write('{}'.format(line))
                else:
                    children.append(os.path.normpath(os.path.join(directory, match.groups()[0])))
                    output.write('#include "{}"\n'.format(os.path.basename(children[-1])))
    for child in children:
        copy_and_resolve(child, target_directory)

# create the build directory
shutil.rmtree(os.path.join(dirname, 'loris'), ignore_errors=True)
os.mkdir(os.path.join(dirname, 'loris'))
copy_and_resolve(os.path.join(dirname, 'source', 'cpp', 'loris_extension.cpp'), os.path.join(dirname, 'loris'))
for name in ['__init__.py', 'config.py', 'CSV.py', 'DAT.py', 'EventStream.py', 'ReadFile.py', 'WriteEventsToFile.py']:
    shutil.copy2(os.path.join(dirname, 'source', name), os.path.join(dirname, 'loris'))

# load data used in setup
def build_ext_factory(parameters):
    import setuptools.command.build_ext
    class build_ext(setuptools.command.build_ext.build_ext):
        def finalize_options(self):
            setuptools.command.build_ext.build_ext.finalize_options(self)
            __builtins__.__NUMPY_SETUP__ = False
            import numpy
            self.include_dirs.append(numpy.get_include())
    return build_ext(parameters)
with open('README.md', 'r') as file:
    long_description = file.read()

# setup the package
setuptools.setup(
    name='loris',
    version='0.2.1',
    url='https://github.com/neuromorphic-paris/loris',
    author='Gregor Lenz, Alexandre Marcireau',
    author_email='gregor.lenz@inserm.fr, alexandre.marcireau@gmail.com',
    description='read and write files from neuromorphic cameras',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['loris'],
    setup_requires=['numpy'],
    install_requires=['numpy'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    ext_modules=[distutils.core.Extension(
        'loris_extension',
        language='c++',
        sources=[os.path.join(dirname, 'loris', 'loris_extension.cpp')],
        extra_compile_args=['-std=c++11'],
        extra_link_args=['-std=c++11'],
        include_dirs=[],
        libraries=(['pthread'] if sys.platform == 'linux' else [])
    )],
    cmdclass={'build_ext': build_ext_factory}
)
