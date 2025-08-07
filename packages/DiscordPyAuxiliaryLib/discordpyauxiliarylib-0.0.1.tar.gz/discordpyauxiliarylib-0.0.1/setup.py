from setuptools import setup, find_packages

setup(
    name='DiscordPyAuxiliaryLib',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'discord.py>=1.7.3',
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