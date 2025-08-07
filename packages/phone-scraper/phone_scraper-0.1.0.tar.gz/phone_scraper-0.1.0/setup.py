from setuptools import setup, find_packages

setup(
    name='phone-scraper',
    version='0.1.0',
    description='Scrape smartphone data from Konga and Jumia',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'pandas',
        'openpyxl',
        'selenium'
    ],
    entry_points={
        'console_scripts': [
            'phone-scraper = phone_scraper.cli:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
