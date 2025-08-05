from setuptools import setup, find_packages

setup(
    name='anno2ls',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='Val Kenneth Arado',
    author_email='aradovalkenneth@gmail.com',
    description='Helper to import images and annotations to Label Studio',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Vaaaaaalllll/anno2ls',
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",  
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

