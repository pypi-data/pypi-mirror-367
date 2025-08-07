from setuptools import setup

setup(
    name='crewai-cache-hook',
    version='0.1.0',
    py_modules=['cache_hook'],
    install_requires=['redis'],
    author='Your Name',
    author_email='your@email.com',
    description='A Redis cache decorator for crewai tasks/flows.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/crewai-cache-hook',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
