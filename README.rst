Whose line is it anyway?
========================

Identify atomic lines in spectra by plotting PHOENIX model spectra
over the NIST Atomic Spectra Database.

Getting started
---------------

Installation
^^^^^^^^^^^^

.. code-block:: bash

    python -m pip install whoseline

Run the app
^^^^^^^^^^^

To run the interactive tool, run:

.. code-block:: bash

    whoseline


Multiple sessions
^^^^^^^^^^^^^^^^^

If you already have an instance of `solara` or `whoseline` running, you can
launch a second one by specifying a different port:

.. code-block:: bash

    whoseline --port 1234
