# This is my simple project
This is the project README.

As said in the LICENCE file, this package is only for use under explicit premission of the GRF team.

The project contains several modules, each one included in only one of the following bins:
A: Structure and general modules, used in all the other modules.
ML: Local modules, related with local run scripts.
MN: Cloud modules, related with cloud run scripts.
Z: Testing modules. Show the structure of the executing code for production in local or cloud environments.

All the required packages are included in setup.py except blpapi (due to legal restrictions). For this package, please use the next code for installing in your local. This package is only used for local processes, so you must not use it in any cloud run function.

py -m pip install --index-url https://blpapi.bloomberg.com/repository/releases/python/simple/blpapi