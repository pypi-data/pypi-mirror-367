from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

# Dummy extension to mark the package as non-pure (platform-specific)
ext_modules = [
    Extension("rmsdynautomationtool.stub", sources=[])
]

# Override build_ext to skip building (since .pyd is prebuilt)
class NoBuildExt(build_ext):
    def run(self):
        pass

setup(
    name="rmsdynautomationtool",
    version="0.0.1.dev01",
    license="Proprietary",
    author="Varchas Solutions Pty Ltd",
    author_email="pritesh.patel@varchassolutions.com.au",
    description="This package is useful for PSS®E power system assessment.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url='https://',
    packages=find_packages(),
    include_package_data=True,
    install_requires = [
        'pillow>=11.2.1',
        'pymupdf>=1.26.3',
        'matplotlib>=3.9.4',
        'numpy>=2.0.2',
        'pandas>=2.3.1',
        'openpyxl>=3.1.5',
        'requests>=2.32.4',
        'scipy>=1.13.1',
        'python-dotenv>=1.1.1',
    ],
    package_data={
        "rmsdynautomationtool": ["**/*.pyd", 
                                 "**/*.py",
                                 "EULA", 
                                 "DISCLAIMER",
                                 ".env", 
                                 ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "License :: Other/Proprietary License",
    ],
    python_requires=">=3.9,<3.13",
    ext_modules=ext_modules,
    cmdclass={"build_ext": NoBuildExt},
)
