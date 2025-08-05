from setuptools import setup, find_packages


# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='3DViewer-Flask',
    version='0.0.2',    
    description='View 3D CAD models with the Python web-framework Flask',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/alekssadowski95/3DViewer-Flask',
    author='Aleksander Sadowski',
    author_email='aleksander.sadowski@alsado.de',
    license='MIT',
    packages=find_packages(),
    install_requires=['Flask'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3'
    ],
)
