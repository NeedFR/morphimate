from setuptools import setup, find_packages

setup(
    name='morphimate',
    version='0.1.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={'': ['*.txt', '*.jpg']},
    scripts=['src/scripts/morphimate_example_1.py', 'src/scripts/morphimate_example_2.py'],
    install_requires=['numpy', 'scipy', 'PyQtX', 'pillow'],
    author='Richard Masterton',
    author_email='r.masterton@gmail.com',
    description='Image morphing utility'
)
