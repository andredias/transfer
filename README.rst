Transfer
========

This project is a Python implementation of `Transfer.sh <https://transfer.sh/>`_,
which is implemented in Go.
It is based on the `FastAPI minimum project template <https://github.com/andredias/perfect_python_project/tree/fastapi-minimum>`_.


Usage
=====

Upload a file:

.. code:: console

    $ http -f POST :5000/ file@/path/to/file
