from __future__ import annotations

import datetime as dt
import json
from functools import lru_cache

from .. import http_ctx, sync_ctx
from .._logging import logger
from .._utils.perf import time_op
from ..progress_reporting import make_download_progress
from . import cataloguer

_LOAD_CATALOGUE_LOCK = '_LOAD_CATALOGUE_'

_base_catalogue_url = (
    f'https://raw.githubusercontent.com/layday/instawow-data/data/'
    f'base-catalogue-v{cataloguer.CATALOGUE_VERSION}.compact.json'
)
_catalogue_ttl = dt.timedelta(hours=4)


@lru_cache(1)
def _parse_catalogue(raw_catalogue: bytes):
    with time_op(lambda t: logger.debug(f'Parsed catalogue in {t:.3f}s')):
        return cataloguer.ComputedCatalogue.from_base_catalogue(
            json.loads(raw_catalogue),
        )


async def synchronise() -> cataloguer.ComputedCatalogue:
    "Fetch the catalogue from the interwebs and load it."
    async with (
        sync_ctx.locks()[_LOAD_CATALOGUE_LOCK],
        http_ctx.web_client().get(
            _base_catalogue_url,
            expire_after=_catalogue_ttl,
            raise_for_status=True,
            trace_request_ctx={
                'progress': make_download_progress(label='Synchronising catalogue')
            },
        ) as response,
    ):
        raw_catalogue = await response.read()

    return _parse_catalogue(raw_catalogue)
