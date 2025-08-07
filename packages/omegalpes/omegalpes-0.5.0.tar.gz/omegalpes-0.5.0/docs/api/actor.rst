actor package
==============

OMEGAlpes offers a library of models associated with the "multi-actor" approach through the Actor package. An explicit actor model aims to differentiate technical issues from stakeholder-induced issues,
and to differentiate the decisions made by the stakeholders. This model does not attempt to model the actors as such but is restricted to the constraints and objectives carried by the actors that influence
the project framework.

It is a matter of being able to differentiate the technical part of the model from the part associated with the actors. When modelling, this approach can lead stakeholders to question
what is technical and what is related to actor's choices. It also helps to provide additional insights in stakeholder negotiations by identifying whether the issues are technical or actor-related.
Negotiation can then be facilitated by the fact that decisions are associated with their stakeholders and their influence on the project can be assessed.

The modeling logic behind actor package is debatable, especially as, by refining the technical considerations, it is possible to take it into account on the energy layer. However, we are convinced that bringing stakeholders into the modelling
loop can facilitate the technical refinement of the energy model and can help decision-making and negotiations between stakeholders.


The actor modelling is based on a main actor class defined on the actor
module.
Then, the actors are divided in two categories: the "operator actors" who
operates energy units and the "regulator actors" who unable to create
regulation constraints.

.. contents::
    :depth: 1
    :local:
    :backlinks: top

Actor module
------------

.. automodule:: omegalpes.actor.actor
    :members:
    :undoc-members:
    :show-inheritance:



The Actor class is defined as an abstract class, i.e. not specific to a particular actor, and has generic methods for adding or removing constraints and goals.
Regarding the constraints, a distinction is made between:

    * definition constraints (DefinitionConstraint), used to calculate quantities or to represent physical phenomena (e.g. storage state of charge) considered a priori as non-negotiable;
    * technical constraints (TechnicalConstraint), used to  represent technical issues (e.g. operating power of a production unit) considered a priori as non-negotiable unless technical changes are made;
    * actor-specific constraints, ActorConstraint and ActorDynamicConstraint, to model a constraint that is due to actor decisions (e.g. minimal level of energy consumption over a period).

Those constraints are exclusive, and only actor-specific constraints are a priori negotiable as decided by the stakeholders themselves. Actors modeling includes additional objectives. In OMEGAlpes, a weight can be added to an objective in order to give more importance to one or more objectives compared to the others.

Area of responsibility
-----------------------

In order to link the energy units to the actors, an area of responsibility is defined for each actor in the model. These are the energy units they operate (for the operating stakeholders) or build (for the developer). From a modelling point of view, this notion of area of responsibility limits the constraints and objectives of the stakeholders, which can only be applied to the area of responsibility of the latter. To do so , it is necessary to define the stakeholder's responsibility space in the modelling by using two attributes associated to the Actor class:

    * operated_unit_list : to indicate the energy units within the stakeholder's area of responsibility,
    * operated_node_list : to indicate which nodes are part of the stakeholder's area of responsibility.

Operator_actors module
----------------------

.. automodule:: omegalpes.actor.operator_actors.operator_actors
    :members:
    :undoc-members:
    :show-inheritance:

Operators can only influence - with respect to constraints and objectives - the units within its scope of responsibility, as defined in the following sub-section.
Based on a typology of operator actors, we have developed the following classes: Consumer, Producer, Prosumer, Supplier.



Consumer_actors module
----------------------

.. automodule:: omegalpes.actor.operator_actors.consumer_actors
    :members:
    :undoc-members:
    :show-inheritance:

Consumer class inherits from the the class OperatorActor. It enables
one to model a consumer actor.

Producer_actors module
----------------------

.. automodule:: omegalpes.actor.operator_actors.producer_actors
    :members:
    :undoc-members:
    :show-inheritance:
Producer class inherits from the the class OperatorActor. It enables
one to model an energy producer actor.

Prosumer_actors module
----------------------

.. automodule:: omegalpes.actor.operator_actors.consumer_producer_actors
    :members:
    :undoc-members:
    :show-inheritance:
Prosumer class inherits from the the class OperatorActor, Consumer
and Producer. It enables one to model an actor which is at the same
time an energy producer and consumer

Regulator_actors module
-----------------------

.. automodule:: omegalpes.actor.regulator_actors.regulator_actors
    :members:
    :undoc-members:
    :show-inheritance:

Regulators do not operate any particular energy unit but influence the energy system with regard to grid and/or resource regulation. Their decisions can affect all energy units.
From a modelling point of view, we have modelled the RegulatorActor class which inherits from the Actor class.

The regulatory actors are divided into two main categories: local regulatory authorities (e.g. local authorities) and regulatory authorities outside the project (e.g. State, National Energy Regulator entities, such as CRE in France),
respectively modelled by the classes LocalAuthority and StateAuthority.
