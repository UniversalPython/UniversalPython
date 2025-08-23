universalpython_kernel
===========

> Run UniversalPython code in Jupyter Notebook

``universalpython_kernel`` is a simple wrapper over Jupyter's IPython kernel. It simply translates the code from human language to English before passing it on to IPython.

You can learn more about wrapper kernels here:

http://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html

Installation
------------
To install ``universalpython_kernel`` from this repository::

    git clone <LINK TO THIS REPO>
    cd universalpython_kernel
    pip install -e .
    python setup.py install
    python -m universal_python.install

Using the UniversalPython kernel
---------------------
**Notebook**: The *New* menu in the notebook should show an option for an UniversalPython notebook.

**Console frontends**: To use it with the console frontends, add ``--kernel universalpython`` to
their command line arguments.

How to select a human language
------------------------------
You can specify the language for your code by adding a special comment at the top of your file or cell:

    # language: ur

or

    # language: hi

If no language is specified, Urdu (`ur`) will be used by default.
