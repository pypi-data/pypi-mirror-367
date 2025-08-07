from setuptools import setup, find_packages

setup(
    name='tronapisync',
    version='1.0.0',
    packages=find_packages(),
    package_dir={'': '.'},  # Указывает, что пакеты ищутся в текущей директории
    install_requires=[
        'requests',
        'tronpy',
    ],
    description='Tron API verification helper',
    author='Your Name',
    author_email='your.email@example.com',
)