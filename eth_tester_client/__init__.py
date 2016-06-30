import pkg_resources

from gevent import monkey
monkey.patch_all()

from .client import EthTesterClient  # NOQA


__version__ = pkg_resources.get_distribution('ethereum-tester-client').version
