from setuptools import setup

setup(
    name='dateparser_extended',
    version='0.0.2',
    description='Built on Python dateparser library by Scrapinghub, extending it with range detection and fixing Czech '
                'dates recognition.',
    url='https://github.com/ivopisarovic/dateparser-extended',
    author='Ivo Pisarovic',
    author_email='',
    license='MIT',
    packages=['dateparser_extended'],
    install_requires=[
        'dateparser~=1.1.0',
    ],
    classifiers=[],
)