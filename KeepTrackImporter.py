import hdfqs;
import numpy as np;
import re;
from tables import description, Filters, openFile, exceptions;
import xml.etree.ElementTree as et;

class KeepTrackImporter:

  name = "KeepTrack";
  args = [ { "name": "-c", "type": str, "default": None, "help": "Configuration file" }, { "name": "-p", "type": str, "default": None, "help": "HDFQS location" } ];

  def __init__(self, config):
    self.input_filename = config.input_filename;
    self.output_filename = config.output_filename;
    self.tz = config.tz / (60*15);

    self.filters = Filters(complevel=1, complib="zlib", shuffle=True, fletcher32=True);

    self.default_category = "Health";
    self.default_numpy_type = np.float64;
    self.default_pytables_type = description.Float64Col;
    self.watch_config = dict();
    if (config.c is not None):
      self.parse_configuration_file(config.c);
    if (config.p is not None):
      self.hdfqs = hdfqs.HDFQS(config.p);
    else:
      self.hdfqs = None;

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
    table_name = self._table_name(name);
    if (self.hdfqs is not None):
      if (self.hdfqs.exists("self", category, table_name)):
        start_after = self.hdfqs.get_time_range("self", category, table_name)[1];
      else:
        start_after = 0;
    else:
      start_after = 0;

    if (data_type == "number"):
      data = self.parse_number_data(watch, numpy_type, start_after);
      descr = { "time": description.Int64Col(pos=0), "tz": description.Int8Col(pos=1), "value": pytables_type(pos=2) };
      units_attr = { "time": "ns since the epoch", "tz": "15 min blocks from UTC", "value": unit };
    elif (data_type == "marker"):
      data = self.parse_marker_data(watch, start_after);
      descr = { "time": description.Int64Col(pos=0), "tz": description.Int8Col(pos=1) };
      units_attr = { "time": "ns since the epoch", "tz": "15 min blocks from UTC" };
    elif (data_type == "set"):
      ( data, unit ) = self.parse_set_data(watch, start_after);
      descr = { "time": description.Int64Col(pos=0), "tz": description.Int8Col(pos=1), "value": description.Int16Col(pos=2) };
      units_attr = { "time": "ns since the epoch", "tz": "15 min blocks from UTC", "value": unit };
    else:
      print("Unknown KeepTrack data type: %s" % ( data_type ));
      return;

    if (len(data) == 0):
      print("Skipping %s - no data." % ( name ));
      return;
    else:
      print("Importing %s to /self/%s/%s" % ( name, category, table_name ));

    try:
      t = self.fd.getNode("/self/%s/%s" % ( category, table_name ));
    except exceptions.NoSuchNodeError:
      t = self.fd.createTable("/self/%s" % ( category ), table_name, descr, name, filters=self.filters, createparents=True);
      t.attrs["units"] = { "time": "ns since the epoch", "tz": "15 min blocks from UTC", "value": unit };
    t.append(data);
    if (not t.cols.time.is_indexed):
      t.cols.time.create_csindex();
    t.flush();

  def parse_number_data(self, watch, numpy_type, start_after):
    data = [ ];
    for value in watch.findall("value"):
      tm = np.int64(value.attrib["time"])*1000000000;
      if (tm <= start_after):
        continue;

      try:
        val = numpy_type(value.text);
      except ValueError:
        print("ERROR importing %s - invalid value \"%s\" for type \"%s\"" % ( name, value.text, str(numpy_type) ));
        exit();

      data.append([ tm, self.tz, val ]);

    return data;

  def parse_marker_data(self, watch, start_after):
    data = [ ];
    for value in watch.findall("value"):
      tm = np.int64(value.attrib["time"])*1000000000;
      if (tm <= start_after):
        continue;
      data.append([ tm, self.tz ]);

    return data;

  def parse_set_data(self, watch, start_after):
    data = [ ];
    values = dict();
    i = 0;
    unit = "";
    for predefined in watch.findall("predefined"):
      values[predefined.text] = i;
      unit = "%s, %d: %s" % ( unit, i, predefined.text );
      i = i + 1;
    unit = unit[2:];

    for value in watch.findall("value"):
      tm = np.int64(value.attrib["time"])*1000000000;
      if (tm <= start_after):
        continue;
      val = values[value.text];
      data.append([ tm, self.tz, val ]);

    return ( data, unit );

  def parse_configuration_file(self, filename):
    try:
      fd = open(filename);
    except IOError:
      print("WARNING - configuration file \"%s\" does not exist." % ( filename ));
      return;

    i = 1;
    while True:
      line = fd.readline().rstrip();
      if (len(line) == 0):
        break;

      tokens = line.split(" ");
      if (len(tokens) < 3):
        print("WARNING - invalid configuration line (line %d)" % ( i ));
        continue;
      cmd = tokens[0];
      if (cmd == "set"):
        self._config_set(tokens[1:], i);
      elif (cmd == "watch"):
        self._config_watch(line, i);
      else:
        print("WARNING - invalid configuration command \"%s\"" % ( cmd ));
    fd.close();

  def _config_set(self, tokens, i):
    config = tokens[0];
    value = tokens[1];
    if (config == "default_category"):
      self.default_category = value;
    elif (config == "default_numpy_type"):
      try:
        self.default_numpy_type = getattr(np, value);
      except AttributeError:
        print("WARNING - invalid numpy type (line %d)" % ( i ));
    elif (config == "default_pytables_type"):
      try:
        self.default_pytables_type = getattr(description, value);
      except AttributeError:
        print("WARNING - invalid PyTables type (line %d)" % ( i ));

  def _config_watch(self, line, i):
    x = re.match("watch \"(.+)\" (.*)", line);
    name = x.group(1);
    tokens = x.group(2).split(" ");
    category = tokens[0];
    try:
      numpy_type = getattr(np, tokens[1]);
    except IndexError:
      numpy_type = None;
    except AttributeError:
      print("WARNING - invalid numpy type (line %d)" % ( i ));
      return;
    try:
      pytables_type = getattr(description, tokens[2]);
    except IndexError:
      pytables_type = None;
    except AttributeError:
      print("WARNING - invalid PyTables type (line %d)" % ( i ));
      return;

    self.watch_config[name] = [ category, numpy_type, pytables_type ];
    
  def _table_name(self, name):
    name = name.replace(" ", "").lower();
    x = re.match("([a-z]+)\(([a-z]+)\)", name);
    if (x is None):
      return name;
    else:
      return "%s_%s" % ( x.group(1), x.group(2) );

  def _table_settings(self, name):
    if (name in self.watch_config):
      return self.watch_config[name];
    else:
      return ( self.default_category, self.default_numpy_type, self.default_pytables_type );
