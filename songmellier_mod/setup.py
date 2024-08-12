from setuptools import setup, find_packages

setup(
    name = 'songmellier_mod',
    version = '0.1',
    packages = find_packages(),
    install_requires = [
        'spotipy',
        'pandas',
        'scikit-learn',
    ],
)