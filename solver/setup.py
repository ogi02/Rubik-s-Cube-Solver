from setuptools import setup, find_packages

setup(
    name="rubik_cube_solver",
    version="0.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
)
