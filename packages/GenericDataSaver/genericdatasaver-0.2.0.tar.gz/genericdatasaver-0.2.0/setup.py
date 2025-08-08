from setuptools import setup, find_packages

setup(
    name='GenericDataSaver',
    version='0.2.0',
    author='MondayStuff',
    author_email='Hoangquocanhmon@icloud.com',
    description='Saves Data, Don\'t use it in production cuz it\'s not secure and it\'s just my hobby project. \n Works with Windows, MacOS, Linux now instead of just MacOS and Linux, Not tested for Windows yet.',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    setup_requires=['setuptools>=61.0'],
    use_pep517=True
)