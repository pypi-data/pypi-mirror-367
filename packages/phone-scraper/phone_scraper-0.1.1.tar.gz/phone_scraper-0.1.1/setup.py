from setuptools import setup, find_packages

setup(
    name='phone_scraper',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'pandas',
        'openpyxl',
        'selenium'
    ],
    author='Irechukwu Nkweke',
    description='Scrape smartphone data from Konga and Jumia',
)
