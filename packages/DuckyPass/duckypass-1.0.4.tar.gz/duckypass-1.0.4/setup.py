from setuptools import setup, find_packages

setup(
    name="DuckyPassAPI",
    version="1.0.4",
    description="A Python module for generating passwords using the DuckyPass API.",
    author="Rhys Wills",
    author_email="rhys@rwills.net",
    license="gpl3",
    packages=find_packages(),
    install_requires=["requests"],
    url="https://github.com/maxrhys/PythonDuckyPassAPI",
    keywords=["password", "generator", "API", "DuckyPass"],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)