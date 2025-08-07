from setuptools import setup, find_packages

setup(
    name='imageops_sribalajiSTR',
    version='0.1.0',
    description='Custom image processing operators: point, filter, histogram, etc.',
    author='SRI BALAJI P _ STR',
    author_email='sribalajipurushothaman@gmail.com',
    packages=find_packages(),  
    install_requires=[
        'opencv-python',
        'numpy',
        'matplotlib'
    ],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
