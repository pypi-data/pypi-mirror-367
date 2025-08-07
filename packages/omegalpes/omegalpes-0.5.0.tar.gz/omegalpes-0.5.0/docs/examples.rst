How to Use OMEGAlpes
====================

**OMEGAlpes** stands for Generation of Optimization Models As Linear Programming for Energy Systems.
It is an **Open Source** energy systems modelling tool for linear optimisation (LP, MILP).

| **Examples** are developed to help new omegalpes users.
| **Article study cases** are developed for scientific concerns.
They are using a specified graph representation described here: :doc:`OMEGAlpes Representation <OMEGAlpes_graph_representation>`


| To run both, you will first need to install **OMEGAlpes** library.
| To do so, please, have a look to the documentation: :doc:`OMEGAlpes Installation <installation_requirements>`
| Or to the README.md of `OMEGAlpes Gitlab`_

    
Examples
--------

Please have a look to the following examples:

.. contents::
    :depth: 1
    :local:
    :backlinks: top


Example 1: PV self-consumption
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this PV self-consuption example, a single-house with roof-integrated photovoltaic
panels (PV) is studied. Specifically, the study case is about demand-side management
in order to maximize the self-consumption, by shifting two household appliances consumption
(clothes washing machine and clothes dryer) and using a water tank for the
domestic hot water consumption.

| The article presenting this example is available at: `PV self-consumption article`_
| You can access to this example via an online Notebook at: `PV self-consumption online notebook`_
| The code is available here: `PV self-consumption code`_
| The Notebook is available at: `PV self-consumption notebook`_

.. figure::  images/example_PV_self_consumption.png
   :align:   center
   :scale:   55%

   *Figure 1: Principle diagram of the PV self-consumption example | Author: Camille Pajot*

This example leads to a study with :
    - 6922 variables (2890 continuous and 4032 binary)
    - 79172 non-zeros

This optimization problem has been generated within 1.2 seconds on an Intel bicore i5 2.4 GHz CPU.

An optimal solution was found in 43.6 seconds with the free CBC solver available in the PuLP package, and in the 2.5s with the commercial Gurobi solver.


Example 2: Waste heat recovery
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In the waste_heat_recovery module, an electro-intensive industrial process consumes electricity and
rejects heat. This waste heat is recovered by a system composed of a heat pump in order to increase
the heat temperature, and a thermal storage that is used to recover more energy and have a more
constant use of the heat pump. This way, the waste heat is whether recovered or dissipated depending
on the waste heat recovery system sizing. The heat is then injected on a district heat network to
provide energy to a district heat load. A production unit of the district heat network provides the extra
heat.

| The code is available here: `Waste heat recovery code`_
| The Notebook is available at: `Waste heat recovery notebook`_

.. figure::  images/wasteHeatRecovery.PNG
   :align:   center

   *Figure 4: principle diagram of the waste heat recovery example | Author : Camille Pajot*

Technical and decision constraints and objectives can be added to the project. This leads to the following
Figure 5.

.. figure::  images/wasteHeatRecovery_withConstraints.PNG
   :align:   center
   :scale:   80%

   *Figure 6: principle diagram of the waste heat recovery example with constraints | Author: Camille Pajot*

Applying, multi-stakeholder vision on the waste heat recovery project leads to the Figure 6.
One central point is the governance of the storage and heat pump. Who's financing it? which actor
will operate it? This governance needs to be discuss and mutually agreed to be able to go further on the project.

.. figure::  images/wasteHeatRecovery_multiStakeholders.PNG
   :align:   center
   :scale:   80%

   *Figure 6: principle diagram of the waste heat recovery example with multi-stakeholder vision | Author: Lou Morriet from Camille Pajot work*


A technical optimisation over one year on a hourly time step can lead to a study with
    - 228k variables (158k continuous et 70k binaires)
    - 316k constraints
It has been solved in 13h with Gurobi, which can be considered as correct considering the high number of variables
and constraints.

Considering the 20MWh / 6.7MW storage this can of study can calculate that
60% of the annual needs could be covered by the LNCMI waste heat
(which corresponds to 60% reduction in CO2 emissions)
/!\ This outputs should be consider regarding the constraints and objectives of the model,
which are not totally detailed here, as the goal of this part is to show the possibilities of OMEGAlpes.

Graphics like the following one can also be produced:

.. figure::  images/wasteHeatRecovery_study.PNG
   :align:   center
   :scale:   80%

   *Figure 7: heat provider of the district over a year | Author: Camille Pajot*


Various studies could be carried out:
    - Balancing between CO2 emissions from the LNCMI and district heating, free profile
    - Using HP according to the electricity price, typical profiles
    - Study of operational performances under constraints, fixed profile



How to Run an Example
---------------------

The example codes are stored at the Gitlab: `OMEGAlpes Examples`_ in the folder "beginner_examples" or "examples".
Some of them have also been developed on a Jupyter notebook for a better understanding.

.. Note:: To know how to run the example python codes or the notebooks, see:
            `Help run Jupyter Notebook`_ 

            | Run notebooks with Binder: `Help run Notebook with mybinder`_ 
            | Run the examples: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_notebooks


.. Note:: The examples may be updated with the last **developer** version which
   may be different from the OMEGAlpes **user** (Pypi) version.
   Thus, you may have to run the examples with the developer version.
   Otherwise you have to select the example version corresponding to the
   current Pypi version. The version used is indicated at the beginning
   of the example module.

In order to run example, you first need to download (or clone) the OMEGAlpes Examples folder (repository) at :
`OMEGAlpes Examples`_.
In fact, it is better to download the whole folder as most of the examples
or article case studies use data located outside the code file.

Then, open your development environment, select the example file you want (`.py`) and run it.

.. Note:: **Do not forget:**
          To run your example, you first need to install **OMEGAlpes** library.
          To do so, please, have a look to the documentation: :doc:`OMEGAlpes Installation <installation_requirements>`
          Or to the README.md of `OMEGAlpes Gitlab`_

.. contents::
    :depth: 3
    :local:
    :backlinks: top


Model Templates
---------------

*This page is under development and wil be updated*

OMEGAlpes use principles will be detailed here.

**Please click on the following link to have a look to
OMEGAlpes examples and study cases:**
`OMEGAlpes Examples Documentation`_


.. _OMEGAlpes Examples Documentation: https://omegalpes-examples.readthedocs.io/

In the meantime, empty templates for creating OMEGAlpes models including
actors or not are available in this OMEGAlpes examples folder: `Templates`_


A `tutorial`_ with linked notebooks are also available.

The `notebook folder`_ also enable to discover OMEGAlpes functionnalities, and
especially `this notebook about waste heat recovery`_.



.. _tutorial: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples/-/blob/master/tutorials/Tutorial_OMEGAlpes_2020.md
.. _notebook: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples/-/blob/master/notebooks/To_Modify__PV_self_consumption_eng.ipynb
.. _notebook folder: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples/-/tree/master/notebooks
.. _this notebook about waste heat recovery: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples/-/blob/master/notebooks/article_2021_MPDI_waste_heat.ipynb
.. _OMEGAlpes Gitlab: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes/-/blob/master/README.md
.. _OMEGAlpes Installation: https://omegalpes.readthedocs.io/en/stable/installation_requirements.html
.. _OMEGAlpes Examples: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples
.. _PV self-consumption online notebook: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples/-/blob/master/notebooks/To_Modify__PV_self_consumption_eng.ipynb
.. _PV self-consumption notebook: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_notebooks/blob/master/notebooks/article_2019_BS_PV_self_consumption.ipynb
.. _PV self-consumption code: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples/-/tree/master/various_examples/beginner_examples/PV_self_consumption
.. _PV self-consumption article: http://hal.univ-grenoble-alpes.fr/hal-02285954v1
.. _Electrical system operation code: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples/blob/master/beginner_examples/electrical_system_operation.py
.. _Electrical system operation notebook: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_notebooks/blob/master/notebooks/electrical_system_operation.ipynb
.. _Storage design code: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples/blob/master/beginner_examples/storage_design.py
.. _Storage design notebook: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_notebooks/blob/master/notebooks/storage_design.ipynb
.. _Waste heat recovery code: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples/-/tree/master/various_examples/beginner_examples/waste_heat_recovery
.. _Waste heat recovery notebook: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_notebooks/blob/master/notebooks/waste_heat_recovery.ipynb
.. _NoteBook: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes-notebooks
.. _Help run Jupyter Notebook: https://omegalpes-examples.readthedocs.io/en/latest/jupyter.html
.. _Help run example: https://omegalpes-examples.readthedocs.io/en/latest/examples_run.html
.. _BS2019 PV self-consumption code: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples/blob/master/article_case_study/article_2019_BS_PV_self_consumption.py
.. _PV self-consumption notebook: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_notebooks/blob/master/notebooks/article_2019_BS_PV_self_consumption.ipynb
.. _PV self-consumption article: http://hal.univ-grenoble-alpes.fr/hal-02285954v1
.. _BS2019 multi-actor Modelling code: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples/-/tree/master/article_case_study/article_2019_BS_multi_actor_modelling
.. _BS2019 multi-actor Modelling article: http://hal.univ-grenoble-alpes.fr/hal-02285965v1
.. _BS2019 multi-actor Modelling notebook: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_notebooks/blob/master/notebooks/article_2019_BS_multi_actor_modelling.ipynb


.. _OMEGAlpes Documentation: https://omegalpes.readthedocs.io/
.. _OMEGAlpes Installation: https://omegalpes.readthedocs.io/en/stable/installation_requirements.html
.. _OMEGAlpes Examples: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples
.. _OMEGAlpes Representation: https://omegalpes.readthedocs.io/en/latest/OMEGAlpes_graph_representation.html
.. _Templates: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes_examples/-/tree/master/case_study_template
.. _Help run Notebook with mybinder: https://mybinder.org/v2/git/https%3A%2F%2Fgricad-gitlab.univ-grenoble-alpes.fr%2Fomegalpes%2Fomegalpes_notebooks/HEAD