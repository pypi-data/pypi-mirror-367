from setuptools import setup, find_packages

setup(
    name='kstflow',
    version='0.1.44',
    packages=find_packages(),
    install_requires=[
        'requests',
        'tqdm',
        'matplotlib',
        'pillow',
        'opencv-python',
        'tensorflow-cpu',
        'numpy', 
    ],
    include_package_data=True,
    description='KST AI Utilities for medical datasets',
    author='Watcharaphong Yookwan',
    author_email='kst@informatics.buu.ac.th',
    url='https://kst.buu.ac.th',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
