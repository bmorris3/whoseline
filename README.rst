Whose line is it anyway?
========================

Identify atomic lines in spectra by plotting PHOENIX model spectra
over the NIST Atomic Spectra Database.

Install and run locally
-----------------------

.. code-block:: bash

    python -m pip install git+https://github.com/bmorris3/whoseline
    whoseline

If you already have an instance of `solara` or `whoseline` running, you can
launch a second one by specifying a different port:

.. code-block:: bash

    whoseline --port 1234
