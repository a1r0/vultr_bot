from setuptools import setup
""""
TODO: write setup.py scripts
"""

setup(
    name='vultr_bot',
    author='A1r0',
    version='0.1',
    install_requires=[
        'hurry.filesize',
        'python-telegram-bot'
    ],
)

if __name__ == "__main__":
    setup()