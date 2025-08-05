from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# 获取长描述
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='aidesk',
    version='0.2.a',
    description='A simple web service with file operations and instance management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/aidesk',
    author='Your Name',
    author_email='your.email@example.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='web service, file management, instance management',
    packages=find_packages(exclude=['tests']),
    python_requires='>=3.6, <4',
    entry_points={
        'console_scripts': [
            'aidesk=aidesk.cli:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/aidesk/issues',
        'Source': 'https://github.com/yourusername/aidesk/',
    },
    include_package_data=True,
)
