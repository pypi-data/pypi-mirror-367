# setup.py

from setuptools import setup, find_packages

setup(
    name='neritya_clock',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],  # Add dependencies here if any
    entry_points={
        'console_scripts': [
            'neritya_clock = neritya_clock.main:main'
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A terminal-based clock application',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/neritya_clock',  # Create and link your GitHub repo here
    classifiers=[
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
