import os

# This is gross, and ther ehas to be a better way,
# but apparently the location of this file differs
# when installed via pypi...
file = os.path.join(os.path.dirname(__file__), "VERSION")
if os.path.isfile(file) is False:
    file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "VERSION");

VERSION = open(file).read().strip()
