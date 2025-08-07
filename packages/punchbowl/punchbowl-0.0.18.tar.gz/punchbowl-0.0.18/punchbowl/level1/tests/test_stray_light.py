import pathlib
from datetime import UTC, datetime

import numpy as np
import pytest
from ndcube import NDCube
from prefect.logging import disable_run_logger

from punchbowl.data.tests.test_punch_io import sample_ndcube
from punchbowl.exceptions import LargeTimeDeltaWarning
#from punchbowl.exceptions import InvalidDataError
from punchbowl.level1.stray_light import remove_stray_light_task

THIS_DIRECTORY = pathlib.Path(__file__).parent.resolve()


def test_no_straylight_file(sample_ndcube) -> None:
    """
    An invalid vignetting file should be provided. Check that an error is raised.
    """

    sample_data = sample_ndcube(shape=(10, 10), code="CR1", level="0")
    straylight_before_filename = None
    straylight_after_filename = None

    with disable_run_logger():
        corrected_punchdata = remove_stray_light_task.fn(sample_data, straylight_before_filename, straylight_after_filename)
        assert isinstance(corrected_punchdata, NDCube)
        assert corrected_punchdata.meta.history[0].comment == 'Stray light correction skipped'
