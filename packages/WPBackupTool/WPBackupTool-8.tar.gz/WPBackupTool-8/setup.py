import setuptools

setuptools.setup(
    name="WPBackupTool",
    version="8",
    author="Sascha Huber",
    author_email="kontakt@sascha-huber.com",
    description="Create Backups of your Wordpress-Site with ease!",
    long_descritpion="Backup-Tool for Wordpress",
    long_description_content_type="text/markdown",
    url="https://github.com/dersaschahuber/WPBackupTool",
    entry_points = {
        'console_scripts': ['WPBackupTool=WPBackupTool.CommandLine:main'],
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'paramiko'
    ]
)

#Commands to build
#pip install --upgrade setuptools wheel twine
