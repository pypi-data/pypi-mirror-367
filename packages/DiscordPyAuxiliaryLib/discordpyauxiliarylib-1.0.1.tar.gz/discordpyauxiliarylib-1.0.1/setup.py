from setuptools import setup
import re

def derive_version() -> str:
    version = ''
    with open('discord_py_auxiliary_lib/__init__.py') as f:
        version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

    if not version:
        raise RuntimeError('version is not set')

    if version.endswith(('a', 'b', 'rc')):
        # append version identifier based on commit count
        try:
            import subprocess

            p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if out:
                version += out.decode('utf-8').strip()
            p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if out:
                version += '+g' + out.decode('utf-8').strip()
        except Exception:
            pass

    return version

NAME = 'DiscordPyAuxiliaryLib'

PACKAGES = [
    'discord_py_auxiliary_lib',
    'discord_py_auxiliary_lib.select'
]

setup(
    name=NAME,
    version=derive_version(),
    packages=PACKAGES,
    install_requires=[
        'discord.py>=2.5.2',
        # Add other dependencies here
    ],
    author='hashimotok',
    author_email='contact@hashimotok.dev',
    url='https://github.com/hashimotok-ecsv/DiscordPyAuxiliaryLib',
    download_url='https://github.com/hashimotok-ecsv/DiscordPyAuxiliaryLib',
    python_requires=">=3.10.6",
    description='A library to assist with Discord.py development',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    keywords='discord.py auxiliary library',
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'discord-py-auxiliary-lib=discord_py_auxiliary_lib.__main__:main',
        ],
    },
    project_urls={
        'Documentation': 'https://discord-py-auxiliary-lib.readthedocs.io/',
        'Source': 'https://github.com/hashimotok-ecsv/DiscordPyAuxiliaryLib',
        'Tracker': 'https://github.com/hashimotok-ecsv/DiscordPyAuxiliaryLib/issues',
    },
    license='MIT',
    license_files=('LICENSE',),
)