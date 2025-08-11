Quick Start
===========
The primary usage of this library is to generate dat files from a given knitout program or generate knitout programs from a given dat file.
This functionality is accessed through the following function calls.

Knitout->Dat
------------

.. code-block:: python

   from knitout_to_dat_python.knitout_to_dat import knitout_to_dat

   dat_file = knitout_to_dat("your_knitout_program.k", "the_dat_file.dat")

Dat->Knitout
------------

.. code-block:: python

   from knitout_to_dat_python.knitout_to_dat import dat_to_knitout

   knitout_file = dat_to_knitout("your_dat_file.dat", "your_knitout_file.k")
