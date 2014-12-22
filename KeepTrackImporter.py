class KeepTrackImporter:

  name = "KeepTrack";
  args = [ { "name": "-c", "type": str, "default": None } ];

  def __init__(self, config):
    self.input_filename = config.input_filename;
    self.output_filename = config.output_filename;
    self.tz = config.tz;

    self.filters = Filters(complevel=1, complib="zlib", shuffle=True, fletcher32=True);
