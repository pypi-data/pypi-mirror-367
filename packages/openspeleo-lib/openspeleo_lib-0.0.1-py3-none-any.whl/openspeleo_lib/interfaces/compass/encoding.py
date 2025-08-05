import contextlib
import logging
from pathlib import Path

from openspeleo_core.legacy import serialize_dict_to_xmlfield
from openspeleo_core.mapping import apply_key_mapping

from openspeleo_lib.debug_utils import write_debugdata_to_disk
from openspeleo_lib.interfaces.compass.name_map import COMPASS_MAPPING

logger = logging.getLogger(__name__)
DEBUG = False


def compass_encode(data: dict) -> dict:
    # ==================== FORMATING FROM OSPL TO TML =================== #

    # 4. Apply key mapping in reverse order
    data = apply_key_mapping(data, mapping=COMPASS_MAPPING)

    if DEBUG:
        write_debugdata_to_disk(data, Path("data.export.mapped.json"))

    # ------------------------------------------------------------------- #

    return data
