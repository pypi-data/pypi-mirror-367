Energy flexibility features
===========================

To summarise the flexibility capabilities of Energy Units in OMEGAlpes:

- You can directly use the following parameters when creating an Energy Unit:

 - min_time_on / min_time_off: to define the minimum time the unit must be operating / not operating once started up / once switched off.
 - availability_hours: to define the number of hours the energy unit is available on the whole time horizon.
 - e_min: to set the minimal energy the unit must consume during the time horizon
 - e_max: to set the maximal energy the unit can consume during the time horizon
 - The ramp rates min_ramp_up, max_ramp_up, min_ramp_down, max_ramp_down

- As a user you can also define a Shiftable Energy unit, you need to choose a power profile that can be shifted in time (so shorter in time than your time horizon, for instance a 2 hours power profile of a washing machine cycle compared to a 24 hours time horizon) and to define if the operation of the energy unit is mandatory or not.

- Finally, you can use the functions:

 - add_operating_time_range to define a range of hours during which the energy  unit can be operated every day.
 - add_energy_limits_on_time_period to define a minimal or maximal energy limit on a given time period of the studied horizon.

Some key articles in open access regarding OMEGAlpes and its use for flexibility studies:

- Residential energy flexibility in districts:

 - `An Approach to Study District Thermal Flexibility Using Generative Modeling from Existing Data`_, Pajot et al.
 - `Impact of Heat Pump Flexibility in a French Residential Eco-District`_, Pajot et al.
 - `Building Reduced Model for MILP Optimization, Application to Demand Response of Residential Buildings`_, Pajot et al.

- Industrial energy flexibility in districts:

 - `Data-driven Modeling of Building Consumption Profile for Optimal Flexibility, Application to Energy Intensive Industry`_, Pajot et al.

.. _An Approach to Study District Thermal Flexibility Using Generative Modeling from Existing Data: https://hal.archives-ouvertes.fr/hal-02509491
.. _Impact of Heat Pump Flexibility in a French Residential Eco-District: https://hal.archives-ouvertes.fr/hal-02278131
.. _Building Reduced Model for MILP Optimization, Application to Demand Response of Residential Buildings: https://hal.archives-ouvertes.fr/hal-02364704
.. _Data-driven Modeling of Building Consumption Profile for Optimal Flexibility, Application to Energy Intensive Industry: https://hal.archives-ouvertes.fr/hal-02364669