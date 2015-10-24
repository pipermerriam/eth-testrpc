# Get the version from the file if the file exists.
# If the file doesn't exist, that means we're running from pypi.

import pkg_resources
import os

file = os.path.join(os.path.dirname(__file__), "../VERSION")
if os.path.isfile(file) is True:
    version = open(file).read().strip()
else:
    version = pkg_resources.get_distribution("eth-testrpc").version

VERSION = version
