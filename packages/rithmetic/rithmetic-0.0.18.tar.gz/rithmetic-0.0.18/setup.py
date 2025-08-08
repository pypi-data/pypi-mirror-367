from setuptools import setup, find_packages
from setuptools.command.egg_info import egg_info


class egg_info_ex(egg_info):
    """Includes license file into `.egg-info` folder."""

    def run(self):
        # don't duplicate license into `.egg-info` when building a distribution
        if not self.distribution.have_run.get('install', True):
            # `install` command is in progress, copy license
            self.mkpath(self.egg_info)
            self.copy_file('LICENSE.md', self.egg_info)

        egg_info.run(self)


with open("README.md", "r", encoding='UTF-8') as f:
    long_description = f.read()

setup(
    name= 'rithmetic',
    version= '0.0.18',
    packages= find_packages(),
    install_requires= [],
    description= "Simple arithmetic lib for students",
    long_description=long_description,
    long_description_content_type= "text/markdown",
    url= "https://github.com/Prashant-Aswal/rithmetic",
    author= "PrashantAswal",
    author_email= "prashant.aswal89@gmail.com",
    license= "MIT",
    license_files= ("LICENSE.md",),
    cmdclass= {'egg_info': egg_info_ex},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "rith = rithmetic:welcome",
            "rith-version = rithmetic:ver",
        ],
    },
)