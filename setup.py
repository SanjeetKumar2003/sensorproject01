from setuptools import find_packages, setup
from typing import List

def get_requirements(file_path: str) -> List[str]:
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace("\n", "") for req in requirements]
    return requirements    

setup(
    name='fault_detection',
    version='0.0.1',
    author='Sanjeet Kumar',
    author_email='skssanjeet9835@gmail.com',
    install_requires=get_requirements('requirements.txt'),  # Corrected here
    packages=find_packages()
)
