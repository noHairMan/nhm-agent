import os

from mercedes.utils.functional import SimpleLazyObject


def _get_settings():
    from dynaconf import Dynaconf

    return Dynaconf(
        envvar_prefix=os.environ.get("MERCEDES_APP"),
        settings_files=["/".join(os.environ.get("MERCEDES_SETTINGS_MODULE", "").split(".")) + ".py"],
        load_dotenv=True,
    )


settings = SimpleLazyObject(_get_settings)
