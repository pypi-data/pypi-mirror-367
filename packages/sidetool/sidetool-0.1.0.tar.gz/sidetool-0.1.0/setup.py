from setuptools import setup, find_packages

setup(
    name='sidetool',
    version='0.1.0',
    description='Helper tools for PySide6 and PyInstaller builds',
    author='Alan Lilly',
    packages=find_packages(),  # Automatically includes `sidetool` folder
    include_package_data=True,
    install_requires=[
        'PyInstaller>=5.8.0',
    ],
    entry_points={
        'console_scripts': [
            'sidetool.build=sidetool.build:main',
            'sidetool.clean=sidetool.clean:main',
            'sidetool.compile=sidetool.compile:main',
            'sidetool.run=sidetool.run:main',
        ],
    },
)
