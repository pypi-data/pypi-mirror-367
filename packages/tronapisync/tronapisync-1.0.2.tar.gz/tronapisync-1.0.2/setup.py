from setuptools import setup, find_packages

setup(
    name="tronapisync",
    version="1.0.2",  # Увеличьте версию!
    packages=find_packages(),
    package_data={'tronapisync': ['*.py', '*.json']},  # Если есть доп файлы
)