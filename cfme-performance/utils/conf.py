from py.path import local
from yaycl import Config
import os
import sys

base_dir = local(os.path.abspath(__file__)).new(basename='..')
yaycl_options = {
    'config_dir': base_dir.join('conf').strpath,
    'extension': '.yml'
}

sys.modules[__name__] = Config(**yaycl_options)
