__version__ = '0.0.1.dev23'

try:
    from importlib.metadata import version
    __version__ = version("solidkit")
except:
    pass
