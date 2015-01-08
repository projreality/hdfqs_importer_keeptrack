Configuration File Syntax
=========================

The configuration file controls how HDFQS KeepTrack Importer handles numeric data, and how the data is ultimately stored in HDFQS. There are three aspects of each tracker that require configuration:

- Category - what category (under the :literal:`self` location) the data table will be in. The default is :literal:`Health`.
- NumPy type - what NumPy type is used to convert the numeric data from strings. The default is :literal:`float64`.
- PyTables type - what column type is used in PyTables to store the data. The default is :literal:`Float64Col`.

To override the default values, use :literal:`set` command in the configuration file::

  set default_category {Category}
  set default_numpy_type {NumPy Type}
  set default_pytables_type {PyTables Column Type}

The defaults can also be overriden on a per-tracker basis using the :literal:`watch` command::

  watch "{Name}" {Category} {NumPy Type} {PyTables Column Type}

All words in a command must be separated by a single space. All commands must be separated by a newline.

For example, given the configuration file below::

  set default_category Exercise
  set default_numpy_type int16
  set default_pytables_type Int16Col
  watch "Weight" Health float64 Float64Col

Tables containing the imported data will be placed in :literal:`/self/Exercise` by default. Data will be converted from strings into :literal:`np.int16` by default. Data will be stored in :literal:`tables.Int16Col` columns in PyTables by default. However, data from the Weight tracker will be converted to :literal:`np.float64` and stored in a :literal:`tables.Float64Col` column, and the table will be placed in :literal:`/self/Health`.
