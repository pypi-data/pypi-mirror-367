About OMEGAlpes
===============

OMEGAlpes is a linear optimization tool designed to easily generate multi-carrier energy system models. Its purpose is to assist in developing district energy projects by integrating design and operation in pre-studies phases.
OMEGAlpes is open-source and written in Python with the licence `Apache 2.0`_.
It is a generation model tool based on an intuitive and extensible object-oriented library that aims to provide a panel of pre-built energy units with predefined operational options, and associated constraints and objectives taking into account stakeholders.


OMEGAlpes Features
-------------------

The development of OMEGAlpes meets a number of objectives, which will call on specific features:

- simplicity and speed of use,

- multi-energy,

- generic (i.e. capable of handling a variety of study cases),

- extensible and reusable,

- compatible with MILP (Mixed Integer Linear Programming) formulation.


OMEGAlpes is developed in order to provide various features regarding energy system optimization, and especially energy flexibility:

.. toctree::
   :maxdepth: 2

   api/flexibility

OMEGAlpes was also presented and used in several scientific publications that can be found here:

.. toctree::
   :maxdepth: 2

   api/publications

Partners
---------
OMEGAlpes is mainly developped in the Grenoble Elctrical Engineering Laboratory (University Grenoble Alpes, CNRS, Grenoble INP, G2Elab, F-38000 Grenoble, France).

Other teams took part in the tool development:

- LOCIE (Laboratoire Optimisation de la Conception et Ingénierie de l’Environnement (LOCIE), CNRS UMR 5271—Université Savoie Mont Blanc, Polytech Annecy-Chambéry, Campus Scientifique, Savoie Technolac, CEDEX, 73376 Le Bourget-Du-Lac,) in thermal engineering for the exergy package in particular

- PACTE (Université Grenoble-Alpes, UMR 5194 PACTE) in social sciences for the actors package in particular

- MIAGE (Master Méthodes informatiques appliquées à la gestion des entreprises, Université Grenoble-Alpes) master students in computing for the GUI development.

- `LNCMI`_ (Le Laboratoire National des Champs Magnétiques Intenses)

History and Open Source Development
-----------------------------------

The development of OMEGAlpes began in 2015 under the impetus of Vincent Reinbold, and was then taken up again in 2017, particularly in the thesis work of Camille Pajot, 
who really laid the foundations of the tool, particularly as applied to the challenges of energy flexibility at neighbourhood level. 
Then Lou Morriet, in partnership with Grenoble's PACTE social science laboratory, developped a library based on stakeholders and 
in particular their scope of responsibility.  Mathieu Brugeron also used the tool on an optimised predictive controller application, 
and Sacha Hodencq on the development of a library of case studies. From 2024, the tool has been used in the `FlexRICAN`_ european project 
in Séverin Valla PhD as well as Nana Kofi and Mainak Dan post-doctoral work, to study the energy flexibility of research infrastructures.  

The choice of open-source was made when the work was resumed in 2017, with a view to accessibility and maximising the potential for collaboration. 
A permissive licence, `Apache 2.0`_, was therefore selected to enable collaboration, including with stakeholders who had opted for a proprietary 
development strategy. The tool has been versioned online since 2018, with examples of use and notebooks on the Gitlab software forge, 
and archived on Software Heritage. Its documentation is available online. OMEGAlpes leaves the choice of solver to the user via 
the PuLP package: the use of open-source solvers does not limit accessibility to professionals or academic users, while the possibility
of using open-source solvers does not limit accessibility to professionals or academic users.

Authors:
--------
See `AUTHORS in OMEGAlpes repository`_.


Acknowledgments
---------------
Vincent Reinbold - Library For Linear Modeling of Energetic Systems : https://github.com/ReinboldV

This work had been partially supported by the `CDP Eco-SESA`_ receiving fund from the French National Research Agency
in the framework of the "Investissements dâ€™avenirâ€ program (ANR-15-IDEX-02) and the VALOCAL project
(CNRS Interdisciplinary Mission and INSIS)

The OMEGAlpes is presently being developed under the work package 6 (`WP6:Energy Flexibility`_) of `FlexRICAN`_ project that is funded by the European Union. The objectives of the WP6 are
to model the multi-energy potential of the flexibility of the 3 research infrastructures (RIs) involved in the project and to quantify the benefit in terms of carbon footprint and services provided to networks of different scales from the European Grid through to the local heating network
and to spread the methods and models developed in this project towards other RI.



.. _`FlexRICAN`: https://flexrican.eu/
.. _`WP6:Energy Flexibility` : https://flexrican.eu/work-package/energy-flexibility/
.. _`Contributors in OMEGAlpes repository`: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes/-/graphs/master
.. _`Apache 2.0`: https://www.apache.org/licenses/LICENSE-2.0.html
.. _`Creative Commons Attribution 4.0 International (CC BY 4.0)`: https://creativecommons.org/licenses/by/4.0/
.. _CDP Eco-SESA: https://ecosesa.univ-grenoble-alpes.fr/
.. _OMEGAlpes Gitlab: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes
.. _OMEGAlpes Examples Documentation: https://omegalpes_examples.readthedocs.io/
.. _OMEGAlpes interface: https://mhi-srv.g2elab.grenoble-inp.fr/OMEGAlpes-web-front-end/
.. _`AUTHORS in OMEGAlpes repository`: https://gricad-gitlab.univ-grenoble-alpes.fr/omegalpes/omegalpes/-/blob/master/AUTHORS.rst
.. _`LNCMI`: https://lncmi.cnrs.fr/