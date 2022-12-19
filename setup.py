import setuptools

requirements = open('requirements.txt').read().splitlines()

setuptools.setup(
    name='lumix_control',
    version='0.0.3',
    author='tarneaux',
    author_email='tarneo@tarneo.fr',
    description='Control Panasonic Lumix cameras',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/tarneaux/lumix-control',
    install_requires=requirements,
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'lumix-control = lumix_control.__main__:main',
            'lc = lumix_control.__main__:main',
        ]
    }
)
