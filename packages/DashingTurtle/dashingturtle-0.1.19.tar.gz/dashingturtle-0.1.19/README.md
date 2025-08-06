🌟 Dashing Turtle Setup & Usage Guide

[![Docs](https://readthedocs.org/projects/dashing-turtle/badge/?version=latest)](https://dashing-turtle.readthedocs.io/en/latest/)

Welcome! This guide will help you install and run the Dashing Turtle application, even if you have little technical background. Just follow each step carefully!

Step 1: Install ViennaRNA for putative structures
DashingTurtle uses the predicted reactivities as constraints in ViennaRNA to calculate putative structures. 

ViennaRNA can be downloaded and installed by following the instructions:
https://www.tbi.univie.ac.at/RNA/ViennaRNA/doc/html/install.html


Step 2: Install Docker (for the database)

Dashing Turtle needs a database to store your data. We use Docker to make this easy and automatic.
✅  macOS

    Download and install Docker Desktop: https://www.docker.com/products/docker-desktop/

    After installing, open Docker Desktop and make sure it’s running.

✅ Linux

    Install Docker Engine: Docker Engine Linux install guide

✔ This will download and start the database in the background.
✔ It will keep your data even after shutting down.

🐍 Step 4: Set up Python environment (local app)
✅ Create a virtual environment

python3.11 -m venv venv

✅ Activate it

    macOS / Linux:

source venv/bin/activate


✅ Upgrade pip

pip install --upgrade pip

✅ Install Dashing Turtle from PyPI

Dashing Turtle is also distributed via PyPI as DashingTurtle. Install it:

pip install DashingTurtle

💻 Step 5: Run the application

✅ Start the Database

dt-db up

✅ Graphical User Interface (GUI)

dt-gui

✅ Command-Line Interface (CLI)

dt-cli

    ✅ You can choose whichever mode you prefer!

🗄️ Database notes

    Your database runs inside Docker and persists data between runs automatically.

    You can stop it any time using:

dt-db down

    To restart:

dt-db up

💬 Help

Please refer to help in the command line interface for more explanation.

🔥 Data Output
Data including landscape files and figures are output to your home directory under 'DTLandscape_Output'


🔥 Sample Data for testing is available at https://github.com/jwbear/Dashing_Turtle.git


## Getting Help

If you run into issues or need troubleshooting advice, please check our [Troubleshooting Guide on Read the Docs](https://dashing-turtle.readthedocs.io/en/latest/docs/troubleshooting.html).


🎉 That’s it!

You’re ready to use Dashing Turtle. Enjoy exploring your data! 🚀
