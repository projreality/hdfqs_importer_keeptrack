KeepTrack Tracker Configuration
===============================

The following are recommendations for configuring your KeepTrack trackers to optimize the importing process.

Name of Tracker
---------------

The name of the tracker should be the name of the value being measured, optionally followed by the source [#f1]_ of the data in parentheses.


For example, the maximum weight achieved on the Bicep Curl machine from the Example manufacturer should be named:

:samp:`Bicep Curl (Example)`

Note that there is a single space between the name of the measurement and the open parenthesis. The general format should be:

:samp:`{Name of measurement} ({Source})`

Units
-----

The unit should be specified as the singular value of the unit. For example, weight lifted in pounds should be :literal:`lb`, amount of water consumed in cups should be :literal:`cup`.

Predefined Values
-----------------

For trackers of type :literal:`Predefined Values`, new values may be added on subsequent imports. However, be sure not to change values already in the list of predefined values, as this may cause previously imported values to be invalid [#f2]_.

.. rubric:: Notes

.. [#f1] The source is often the name or manufacturer of the device performing the measurement (e.g. manufacturer of a weight machine, or name of a heart rate monitor). This makes it simple to record measurements of the same value by multiple devices (e.g. multiple devices measuring steps taken). The name and source should contain only letters, numbers, and the underscore character.

.. [#f2] Values in trackers of type :literal:`Predefined Values` are imported as numbers, and the numbers mapped to the predefined values in the units attribute. Changing the list of predefined values changes this mapping, and causes tables before and after the change to have conflicting number-to-predefined-value maps.
