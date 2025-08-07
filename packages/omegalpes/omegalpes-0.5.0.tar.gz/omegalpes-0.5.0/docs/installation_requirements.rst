OMEGAlpes Installation
======================

.. contents::
    :depth: 1
    :local:
    :backlinks: top

Install OMEGAlpes
-----------------
Do not hesitate to listen to a really nice music to be sure...
... it's going to work!

Python 3.12.0
************
OMEGALpes is developed and tested on Python 3.12.0
`Python 3.12 <https://www.python.org/downloads/release/python-3120/>`_


pip install omegalpes
*********************
Please install OMEGAlpes Lib with pip using on of the following the command prompt:


    - **If you are admin on Windows or working on a virtual environment**::

        pip install omegalpes

    - **If you want a local installation or you are not admin**::

        pip install --user omegalpes

    - **If you are admin on Linux**::

        sudo pip install omegalpes

Then, you can download (or clone) the OMEGAlpes Examples folder (repository) at :
`OMEGAlpes Examples`_
Make shure that the name of the examples folder is: "omegalpes_examples".

Launch the examples (with Pycharm for instance) to understand how the OMEGAlpes Lib works.
Remember that the examples are presented at : :doc:`OMEGAlpes Examples Documentation <examples>`

**Enjoy your time using OMEGAlpes !**



Other installation requirements
-------------------------------
If the music was enough catchy, the following libraries should be
already installed.
If not, increase the volume and install the following libraries
with the help below.

    - **PuLP >= 3.1.1**

    PuLP is an LP modeler written in python.
    PuLP can generate MPS or LP files and call GLPK, COIN CLP/CBC,
    CPLEX, and GUROBI to solve linear problems :
    `PuLP <https://github.com/coin-or/pulp>`_


    - **Matplotlib >= 3.10.3**

    Matplotlib is a Python 2D plotting library :
    `Matplotlib <https://matplotlib.org/>`_


    - **Numpy >= 2.2.6**

    NumPy is the fundamental package needed for scientific computing with Python.
    `Numpy <https://github.com/numpy/numpy>`_


    - **Pandas >= 2.2.3**

    Pandas is a Python package providing fast, flexible, and expressive data
    structures designed to make working with "relational" or "labeled" data
    both easy and intuitive.
    `Pandas <https://pandas.pydata.org/pandas-docs/version/0.23.1/index.html>`_


    ---
    **Command lover**
    --- ::

        pip install <library_name>==version

    If required, the command to upgrade the library is ::

        pip install --upgrade <library_name>

    ---
    **Pycharm lover**
    ---

    Install automatically the library using pip with Pycharm on "File", "settings...", "Project Interpreter", "+",
    and choosing the required library


    ---
    **VS Code lover**
    ---

    Install the library using pip from the integrated terminal: ::

        pip install <library_name>==version

    You can install all dependencies at once from ``requirements.txt`` file: ::

        pip install -r requirements.txt


Install OMEGAlpes as a developer
--------------------------------
Installation as a developer and local branch creation
******************************************************
Absolute silence, `keep calm and stay focused`_... you can do it!

1. Create a new folder in the suitable path, name it as you wish for instance : OMEGAlpes

2. Clone the OMEGAlpes library repository

    ---
    **Command lover**
    --- ::

           git clone https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes.git

    ---
    **Pycharm lover**
    ---

    | Open Pycharm
    | On the Pycharm window, click on "Check out from version control" then choose "Git".
    | A "clone repository" window open.
    | Copy the following link into the URL corresponding area:

        https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes.git

    | Copy the path of the new folder created just before.
    | Test if the connection to the git works and if it works click on "Clone".
    | Once OMEGAlpes is cloned, you must be able to see the full OMEGAlpes library on Pycharm
      or on another development environment.

    ---
    **VS Code lover**
    ---

    | Open Visual Studio Code.
    | On the welcome screen, click on "Clone Git Repository".
    | If the welcome screen doesn't appear, press Ctrl+Shift+P (or Cmd+Shift+P on Mac) to open the Command Palette, then type and select Git: Clone.

    | When prompted for the repository URL, paste the following link:

        https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes.git
    
    | Choose or create a local folder where you want the repository to be cloned.
    | VS Code will start cloning the repository. If successful, it will ask if you want to open the cloned folder — click "Open".
    | You should now see the full OMEGAlpes library in VS Code's Explorer panel.

    If the connection does not work and if you are working with local protected network,
    please try again with the wifi.

3. First, choose or change your project interpreter

    ---
    **Pycharm lover**
    ---

    Click on the yellow warning link or go to "File", "settings...", "Project Interpreter"

    You can:

    - either select the "Python 3.12" project interpreter but you may change the version
      of some library that you could use for another application.

    - either create a virtual environment in order to avoid this problem (recommended).
     | Click on the star wheel near the project interpreter box.
     | Click on "add...".
     | Select "New environment" if it not selected.
     | The location is pre-filled, if not fill it with the path of the folder as folder_path/venv
     | Select "Python 3.12" as your base interpreter
     | Then click on "Ok"

    ---
    **VS Code lover**
    ---

    Click on the interpreter warning in the bottom-left corner of VS Code, or press ``Ctrl+Shift+P`` and choose **"Python: Select Interpreter"**.

    You can:

    - either select the **"Python 3.12"** global interpreter from the list, but you may change the version  
    of some library that you could use for another application.

    - either create a **virtual environment** in order to avoid this problem (recommended). ::

        Open the integrated terminal in VS Code (``Ctrl+` ``).
        Run: ``python3.12 -m venv venv`` (or replace ``python3.12`` with the correct path).
        Activate the environment:
            - On **Windows**: ``venv\Scripts\activate``
            - On **Linux/macOS**: ``source venv/bin/activate``

        VS Code should detect and switch to this environment automatically.
        If not, press ``Ctrl+Shift+P``, search **"Python: Select Interpreter"**,  
        and choose the one that ends with ``/venv``.

4. You can install the library on developing mode using the following command in command prompt
once your are located it on the former folder.
If you are calling OMEGAlpes library in another project, the following command enables you to
refer to the OMEGAlpes library you are developing::

        python setup.py develop

5. If it is not already done, install the library requirements.

    ---
    **Command lover**
    --- ::

            pip install <library_name>

    If required, the command to upgrade the library is ::

            pip install --upgrade <library_name>

    ---
    **Pycharm lover**
    ---

    You should still have a yellow warning.
    You can:

    - install automatically the libraries clicking on the yellow bar.

    - install automatically the library using pip with Pycharm on "File", "settings...", "Project Interpreter", "+",
      and choose the required library as indicated in the Library Installation Requirements
      part.

    ---
    **VS Code lover**
    ---

    You can:

    - install the required library using the integrated terminal.  
    Open the terminal with ``Ctrl+` `` and run ::

        pip install <library_name>==version

    - upgrade the library (if needed) using ::

        pip install --upgrade <library_name>

    - install everything at once from ``requirements.txt`` file with ::

        pip install -r requirements.txt

6. Finally, you can create your own local development branch.

    ---
    **Command lover**
    --- ::

        git branch <branch_name>

    ---
    **Pycharm lover**
    ---

    | By default you are on a local branch named master.
    | Click on "Git: master" located on the bottom write of Pycharm
    | Select "+ New Branch"
    | Name the branch as you convenience for instance "dev_your_name"

    ---
    **VS Code lover**
    ---

    | By default, you are on a local branch named ``master`` or ``main``.  
    | Click on the **branch name** in the bottom-left of VS Code (e.g., ``master``).  
    | Select **"Create new branch..."** from the dropdown.  
    | Name the branch as you prefer, for example: ``dev_your_name``.  
    | The new branch will be created and checked out automatically.
    

7. Do not forget to "rebase" regularly to update your version of the library.

    ---
    **Command lover**
    --- ::

        git rebase origin

    ---
    **Pycharm lover**
    ---

    To do so, click on your branch name on the bottom write of the Pycharm window
    select "Origin/master" and click on "Rebase current onto selected"

    ---
    **VS Code lover**
    ---

    To rebase your local branch onto the latest version of the remote:  
    | Open the **Source Control panel** (or use the Git extension).  
    | Click on the **branch name** in the bottom-left.  
    | Select **"Rebase current branch..."** if available, or open the command palette (``Ctrl+Shift+P``) and run ::

        Git: Rebase Current Branch...

    | Then select the target branch (usually ``origin/master`` or ``origin/main``).

If you want to have access to examples and study cases,
download (or clone) the OMEGAlpes Examples folder (repository) from :
`OMEGAlpes Examples`_ .    \
Make sure that the name of the examples folder is: "omegalpes_examples".
Remember that the examples are presented at : :doc:`OMEGAlpes Examples Documentation <examples>`.


**Enjoy your time developing OMEGAlpes!**


.. _OMEGAlpes Gitlab: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes
.. _OMEGAlpes Examples: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples
.. _keep calm and stay focused: https://www.youtube.com/watch?v=g4mHPeMGTJM