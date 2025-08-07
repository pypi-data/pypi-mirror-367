from setuptools import setup, find_packages

setup(
    name='crewai-cache-hook',
    version='0.1.1',
    packages=find_packages(),
    py_modules=['cache_hook'],
    install_requires=['redis', 'crewai'],
    extras_require={
        'dev': [
            'pytest',
            'coverage',
            'mock'
        ]
    },
    author='Chopper Lee',
    author_email='lihengpro@gmail.com',
    description='A Redis cache decorator for crewAI tasks',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/chopperlee2011/crewai-cache-hook',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    keywords='crewai redis cache decorator',
)
