from setuptools import setup, find_packages

setup(
    name="JoyIT_WLGamepad",
    version="1.0.0",
    description="Library to use the SBC-WLGamepad with the Raspberry Pi",
    author="Joy-IT",
    author_email="service@joy-it.net",
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/joy-it/JoyIT_WLGamepad',  
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    zip_safe=False,
)