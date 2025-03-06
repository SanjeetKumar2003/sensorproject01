from setuptools import find_packages, setup
from typing import List

HYPEN_E_DOT = '-e .'

def get_requirements(file_path: str) -> List[str]:
    """Reads the requirements file and returns a list of dependencies."""
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.strip() for req in requirements]  # Removing newline characters
    
    if HYPEN_E_DOT in requirements:
        requirements.remove(HYPEN_E_DOT)  # Remove '-e .' if present
    return requirements

setup(
    name='Fault Detection',
    version='0.0.1',
    author='Sanjeet Kumar',
    author_email='skssanjeet9835@gmail.com',  # Fixed parameter name from 'author_mail' to 'author_email'
    install_requires=get_requirements('requirements.txt'),  # Fixed 'install_requirements' to 'install_requires'
    packages=find_packages(),
)
