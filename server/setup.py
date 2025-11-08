from setuptools import find_packages, setup

setup(
    name="rubik_cube_server",
    version="0.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
)
