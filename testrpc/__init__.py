import os

# This is gross, and ther ehas to be a better way,
# but apparently the location of this file differs
# when installed via pypi...
VERSION = open(os.path.join(os.path.dirname(__file__), "../VERSION")).read().strip()
