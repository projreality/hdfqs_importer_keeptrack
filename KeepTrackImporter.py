import numpy as np;
import re;
from tables import *;
import xml.etree.ElementTree as et;

class KeepTrackImporter:

  name = "KeepTrack";
  args = [ { "name": "-c", "type": str, "default": None, "help": "Configuration file" } ];

  def __init__(self, config):
    self.input_filename = config.input_filename;
    self.output_filename = config.output_filename;
    self.tz = config.tz / (60*15);

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
    
    data = [ ];
    for value in watch:
      tm = np.int64(value.attrib["time"])*1000000000;

      if (data_type == "number"):
        val = np.float64(value.text);

      if (data_type == "number"):
        data.append([ tm, self.tz, val ]);
      elif (data_type == "marker"):
        data.append([ tm, self.tz ]);

  def _table_name(self, name):
    name = name.replace(" ", "").lower();
    x = re.match("([a-z]+)\(([a-z]+)\)", name);
    if (x is None):
      return name;
    else:
      return "%s_%s" % ( x.group(1), x.group(2) );
