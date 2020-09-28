# Load local options.
import os
from configparser import ConfigParser
options = ConfigParser(
            interpolation=None,
            empty_lines_in_values=False,
          )
options.read(os.path.join(os.path.dirname(__file__), 'local.cfg'))

import config.auth
import config.builders
import config.schedulers
import config.slaves # TODO: Rename slaves to workers
#import status # TODO: status should be renames to something else.
