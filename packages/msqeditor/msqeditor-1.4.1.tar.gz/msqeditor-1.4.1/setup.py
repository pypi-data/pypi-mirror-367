from setuptools import setup, find_packages

setup(
    name='msqeditor',
    version='1.4.1',
    packages=find_packages(),
    include_package_data=True,  # <-- this is required to include files from MANIFEST.in
    install_requires=[
        'asgiref==3.9.1',
        'Django==5.2.4',
        'mysql-connector-python==9.4.0',
        'mysqlclient==2.2.7',
        'PyMySQL==1.1.1',
        'sqlparse==0.5.3',
        'tzdata==2025.2',
    ],
    author='Mentor Misini',
  description=(
    "msqeditor is a Python-based database management editor built with Django, "
    "designed to simplify managing all databases on your VPS through a clean and intuitive web GUI. "
    "It allows easy and secure connections from your local machine using SSH tunnels, "
    "providing a safe way to administer your databases remotely. "
    "Ideal for developers and sysadmins who want a lightweight, customizable tool "
    "to manage databases efficiently with enhanced security."
),
    url='https://github.com/mentormisini/dbeditor.git',
    entry_points={
        'console_scripts': [
            'msqeditor=core.cli:main',
        ],
    }
)
