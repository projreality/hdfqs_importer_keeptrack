import numpy as np;
import re;
from tables import Filters, Float64Col, Int64Col, Int8Col, openFile, exceptions;
import xml.etree.ElementTree as et;

class KeepTrackImporter:

  name = "KeepTrack";
  args = [ { "name": "-c", "type": str, "default": None, "help": "Configuration file" } ];

  def __init__(self, config):
    self.input_filename = config.input_filename;
    self.output_filename = config.output_filename;
    self.tz = config.tz / (60*15);

    self.default_category = "Exercise";
    self.default_numpy_type = np.float64;
    self.default_pytables_type = Float64Col;

    self.filters = Filters(complevel=1, complib="zlib", shuffle=True, fletcher32=True);

  def convert(self):
    pass;

  def import_data(self):
    tree = et.parse(self.input_filename);
    root = tree.getroot();

    self.fd = openFile(self.output_filename, mode="a");

    for watch in root:
      self.import_watch(watch);

    self.fd.close();

  def import_watch(self, watch):
    name = watch.attrib["name"];
    data_type = watch.attrib["type"];
    try:
      unit = watch.attrib["units"];
    except KeyError:
      unit = None;

    ( category, numpy_type, pytables_type ) = self._table_settings(name);

    data = [ ];
    for value in watch:
      tm = np.int64(value.attrib["time"])*1000000000;

      if (data_type == "number"):
        val = numpy_type(value.text);

      if (data_type == "number"):
        data.append([ tm, self.tz, val ]);
      elif (data_type == "marker"):
        data.append([ tm, self.tz ]);

    table_name = self._table_name(name);
    if (len(data) == 0):
      print("Skipping %s - no data." % ( name ));
      return;
    else:
      print("Importing %s to /self/%s/%s" % ( name, category, table_name ));

    try:
      t = self.fd.getNode("/self/%s/%s" % ( self.default_category, table_name ));
    except exceptions.NoSuchNodeError:
      if (data_type == "number"):
        descr = { "time": Int64Col(pos=0), "tz": Int8Col(pos=1), "value": pytables_type(pos=2) };
      elif (data_type == "marker"):
        descr = { "time": Int64Col(pos=0), "tz": Int8Col(pos=1) };
      else:
        print("Unknown KeepTrack data type: %s" % ( data_type ));
        return;
      t = self.fd.createTable("/self/Exercise", table_name, descr, name, filters=self.filters, createparents=True);
      t.append(data);

  def _table_name(self, name):
    name = name.replace(" ", "").lower();
    x = re.match("([a-z]+)\(([a-z]+)\)", name);
    if (x is None):
      return name;
    else:
      return "%s_%s" % ( x.group(1), x.group(2) );

  def _table_settings(self, name):
    return ( self.default_category, self.default_numpy_type, self.default_pytables_type );
