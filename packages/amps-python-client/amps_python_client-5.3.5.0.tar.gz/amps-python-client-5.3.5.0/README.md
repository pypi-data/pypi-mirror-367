AMPS Python Client
==================

Introduction
------------

The AMPS Python Client is a Python extension module that makes it easy to connect to AMPS. This client builds upon the AMPS C++ Client and Python/C api to bring high performance AMPS connectivity to Python code.


Prerequisites
-------------

To use the AMPS Python Client, you must have the following software installed and configured on your system:

* Python 2.7 or Python 3.5 and above.
* Python distutils. Most python installations build and include this package by default, but you may run into issues building this extension module if distutils is not functioning properly on your system.
  Python distutils may be packaged in a standalone package named 'python-distutils', or included in 'python-devel.x86_64'. You can also run the setup script available [here](http://peak.telecommunity.com/dist/ez_setup.py).
* C++ compiler. gcc 4.4 or greater on Linux, or a verion of Visual Studio with Mainstream Support from Microsoft (please
  refer to Microsoft product lifecycle policies) on Windows. Note that this must be the same compiler used to build your
  python distribution, else python distutils may be unable to invoke your compiler.


Fedora prerequisites:
1. dnf install redhat-rpm-config
2. dnf install python-devel  # for use with Python2
3. dnf install python3-devel # for use with Python3
4. dnf install gcc-c++

Building From a Git Clone
-------------------------

If you obtained this client by a git clone of the 60East amps-client-python repository, you also need to fetch the correct version of the 
AMPS C++ client submodule. To do this, issue a git submodule command to initialize and update the src/cpp submodule. One easy
way to do this is by issuing the command:

    git submodule update --init

which will initialize and update the submodule in one step. Note that working with submodules in git requires extra care. Visit
[this chapter](http://git-scm.com/book/en/Git-Tools-Submodules) to learn more about git submodules.

Build
-----

This client is distributed as source code and must be compiled before it is used. The build process emits a shared library
(or DLL on Windows) that can be imported into your python application.

### To build on Linux:

1. Run `python setup.py build` from the AMPS Python Client directory to build the client.

   This script uses Python distutils to build the client library. Python distutils provides many additional options for installing the built library into your Python distribution, or
   otherwise controlling the output of the build process. Run `python setup.py --help` to view command help.

2. Check under the `build` directory for `AMPS.so` -- this is the Python extension module. Ensure this library's directory is in your PYTHONPATH.

3. To test, run `python -c "import AMPS"`.  If any errors occur importing the AMPS module, validate that the module built properly, and that the containing directory is in your PYTHONPATH.

### To build on Windows:

1. Use a Visual Studio Command Prompt to create a command prompt where the necessary Visual Studio environment variables are set for command line builds.

2. Add the Python directory (the location of the python.exe interpreter) to your path.
   *Note:* The platform of your python installation must match the target platform for this python module. If you want to
   build a 64-bit module, you must set your PATH to a 64-bit Python installation; for a 32-bit module, you must set it to
   a 32-bit installation. If you'd like to build both, you must do so separately, once with each Python installation.
3. Run `python setup.py build` fom the AMPS Python Client directory to build the client module. Use the `-p win32` option to build a 32-bit client module.
4. Check under the `build` directory for `AMPS.pyd` -- this is the Python extension module. Ensure this library's directory is in your PYTHONPATH.
5. To test, run `python -c "import AMPS"`. If any errors occur importing the AMPS module, validate that the module built properly, and that the containing directory is in your PYTHONPATH.

Installing the Python Binary Wheel
----------------------------------

60East also provides Linux-x86-64 and Windows 64-bit binary wheels built with Python 2.7 and for Python 3.x.
These wheel files are provided on the 60East website.

If your system is not Linux-x86-64, or you are not using Python 2.6, you can generate your own egg by running 'python setup.py bdist_wheel'.

## Installing:

1. Download the wheel file from the 60East client release page.

2. run 'python -m pip install *.whl'.

Troubleshooting Build Problems
------------------------------

Symptom: Python.h not found

Resolution: Update or install python distutils. See the entry on python distutils in the prequisites section for information on installing this package.


For More Information
--------------------

The developer's guide and generated reference documentation for this client are available under the doc/ directory.

