# setup.py
from setuptools import setup
from setuptools.command.install import install
import subprocess

class PostInstallCommand(install):
    def run(self):
        # Run your post-install script here
        subprocess.call(['python3', '-m', 'groclake_setup_agent.setup_agent'])
        install.run(self)

setup(
    name='groclake_setup_agent',
    version='0.1.4',
    packages=['groclake_setup_agent'],
    install_requires=[
        'requests>=2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'groclake_setup_agent = groclake_setup_agent.setup_agent:main'
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
    },
)
