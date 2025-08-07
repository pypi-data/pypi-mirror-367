OMEGAlpes Graphical Representation
==================================

The energy systems developed in OMEGAlpes are described following
a specified graphical representation.

Representing an energy system
-----------------------------
In order to link the energy units, energy nodes and arrows should
be used. It is possible to highlight the variable which may
be optimised by the system or which is interesting for the user.
Finally, constraints and objectives can be added on the model
with the following representation

.. figure::  images/nodes_flows.png
   :align:   center
   :scale:   40%

   *Figure: Energy Nodes, Flows and Variable of interest representation*


Energy Unit representation
--------------------------
The energy units are described as rectangles as presented just below.

A colour may be added to specify the carrier of the energy unit like
gas (yellow), heat (red), cold (blue), electricity (purple).

.. figure::  images/units_carrier.png
   :align:   center
   :scale:   40%

   *Figure: Connexion and specified carrier energy unit representation*

The symbol is adapted according to the energy unit type.

.. figure::  images/units_fixed_variable.png
   :align:   center
   :scale:   40%

   *Figure: Energy unit representation*

Conversion units use the former representation inside a green box
as multi-carrier energy units. The representation
for ElectricalToHeat, HeatPump and ReversibleConversionUnit are displayed.

Reversible units are represented as single units for simplicity
purpose, even if they do include a production unit and a consumption unit like
conversion units. The power flows of the production and consumption units in
the reversible unit are represented with double arrows, while storage
units' power flow is represented with a single arrow with a double head.
Finally, reversible conversion units are represented based on the former
graphical representations.

.. figure::  images/reversible_and_storage_units.png
   :align:   center
   :scale:   40%

   *Figure: Reversible, storage and reversible conversion units representation*


**Please, have a look to the examples to see if applications of this graphical representation**
:doc:`OMEGAlpes Examples Documentation <examples>`

.. note:: This graph representation is not used yet as a graphical
    user interface but we hope that it will be in the near future.


