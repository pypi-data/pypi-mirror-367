Installation
============

Welcome to the Dashing Turtle installation guide! This document will walk you through setting up and running the Dashing Turtle application, whether you're using Windows, macOS, or Linux.

Step 1: Install ViennaRNA for putative structures
-----------------------------------------

DashingTurtle uses the predicted reactivities as constraints in ViennaRNA to calculate putative structures.

ViennaRNA can be downloaded and installed by following the instructions:
https://www.tbi.univie.ac.at/RNA/ViennaRNA/doc/html/install.html


Step 2: Install Docker (for the database)
-----------------------------------------

Dashing Turtle uses a Dockerized database to store your data. You’ll need Docker installed to run it.

**macOS**

- Download and install Docker Desktop:
  https://www.docker.com/products/docker-desktop

- After installation, launch Docker Desktop and ensure it's running.

**Linux**

- Install Docker Engine following the instructions for your distribution:
  https://docs.docker.com/engine/install/


Step 3: Set Up the Python Environment
-------------------------------------

You’ll now configure the local Python environment for running the app.

**1. Create a virtual environment**

.. code-block:: bash

   python3.11 -m venv myvenv

**2. Activate the environment**

- **macOS / Linux**

  .. code-block:: bash

     source venv/bin/activate


**3. Upgrade pip**

.. code-block:: bash

   pip install --upgrade pip

**4. Install Dashing Turtle from PyPI**

.. code-block:: bash

   pip install DashingTurtle

Step 5: Run the Application
---------------------------
✔ This command will start the database in the background.
✔ Your data will persist across sessions.

.. code-block:: bash

     dt-db up

You can now launch the application in either GUI or CLI mode:

- **Graphical User Interface (GUI)**

  .. code-block:: bash

     dt-gui

- **Command-Line Interface (CLI)**

  .. code-block:: bash

     dt-cli

Choose the mode that best suits your workflow.

Database Management
-------------------

The database runs in Docker and automatically preserves your data.

To stop the database:

.. code-block:: bash

   dt-db down

To start it again:

.. code-block:: bash

   dt-db up

Data Output
-----------

All output files (landscape data, figures, etc.) are saved to:

::

   ~/DTLandscape_Output

Sample Data
-----------

Sample datasets are available here:

https://github.com/jwbear/Dashing_Turtle.git

Help and Support
----------------

Use the `--help` option with CLI commands to see available options and usage:

.. code-block:: bash

   dt-cli --help

You're all set to begin using Dashing Turtle — happy exploring! 🚀
