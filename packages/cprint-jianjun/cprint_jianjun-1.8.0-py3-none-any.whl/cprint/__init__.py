import cprint
import cprint.main
from cprint.tools import demo as _demo  # noqa: F401
from cprint.tools import demoid as _demoid  # noqa: F401
from cprint.tools import getshow_config as _showconfig

__version__ = "1.8.0"

custom_style = {} # 默认自定义样式为空

def _cpshow():  _showconfig(2)
def _cpshoww():  _showconfig(3)

config = cprint = main = tools = None
del config, cprint, main, tools