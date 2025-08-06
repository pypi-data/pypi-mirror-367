from valconfig import ValConfig
from pathlib import Path
from typing import ClassVar

class Config(ValConfig):
    __default_config_path__: ClassVar = "defaults.cfg"

    class paths:
        simresults : Path

config = Config()
