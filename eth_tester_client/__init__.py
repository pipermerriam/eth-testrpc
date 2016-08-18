import pkg_resources

from .client import EthTesterClient  # NOQA


__version__ = pkg_resources.get_distribution('ethereum-tester-client').version
