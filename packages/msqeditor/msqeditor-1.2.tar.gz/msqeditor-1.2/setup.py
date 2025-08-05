from setuptools import setup, find_packages

setup(
    name='msqeditor',
    version='1.2',
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
    description='This editor helps you manage databases on your VPS',
    url='https://github.com/mentormisini/dbeditor.git',
    entry_points={
        'console_scripts': [
            'msqeditor=core.cli:main',
        ],
    }
)
