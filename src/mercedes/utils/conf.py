import os

from dynaconf import Dynaconf

from mercedes import conf

settings = Dynaconf(
    envvar_prefix=conf.APP,
    settings_files=[conf.BASE_DIR / "conf.py"],
    load_dotenv=True,
)
