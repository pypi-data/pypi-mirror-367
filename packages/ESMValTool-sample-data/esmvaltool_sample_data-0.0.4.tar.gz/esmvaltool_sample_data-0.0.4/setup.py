from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

PACKAGES = [
    'esmvaltool_sample_data',
]

setup(
    name='ESMValTool_sample_data',
    version='0.0.4',
    description="ESMValTool sample data",
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Stef Smeets, Bouwe Andela",
    url='https://github.com/ESMValGroup/ESMValTool_sample_data',
    packages=PACKAGES,
    include_package_data=True,
    license="Apache 2.0; CC BY-SA 4.0",
    license_files=("LICENSE",),
    zip_safe=False,
    keywords='ESMValTool',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Hydrology',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    install_requires=[
        'scitools-iris>=3.6',
    ],
    extras_require={
        'develop': [
            'codespell',
            'docformatter',
            'esgf-pyclient',
            'isort',
            'myproxyclient',
            'pre-commit',
            'prospector[with_pyroma]!=1.1.6.3,!=1.1.6.4',
            'pytest',
            'yamllint',
            'yapf',
        ],
    },
)
