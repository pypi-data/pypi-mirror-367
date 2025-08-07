from __future__ import annotations

import datetime as dt
from functools import lru_cache

import cattrs
from attrs import asdict, frozen

from ..definitions import Defn, Strategies, Strategy


def _structure_datetime(value: str | dt.datetime, value_type: type):
    match value:
        case dt.datetime():
            if value.tzinfo != dt.UTC:
                raise ValueError('``datetime`` must be in UTC')
            return value
        case _:
            return dt.datetime.fromisoformat(value).replace(tzinfo=dt.UTC)


def _unstructure_datetime(value: dt.datetime):
    if value.tzinfo != dt.UTC:
        raise ValueError('``datetime`` must be in UTC')

    return value.astimezone(dt.UTC).replace(tzinfo=None).isoformat(' ')


@lru_cache(1)
def make_db_converter():
    converter = cattrs.Converter()
    converter.register_structure_hook(dt.datetime, _structure_datetime)
    converter.register_unstructure_hook(dt.datetime, _unstructure_datetime)
    return converter


@frozen(kw_only=True)
class PkgOptions:
    any_flavour: bool
    any_release_type: bool
    version_eq: bool


@frozen(kw_only=True)
class PkgFolder:
    name: str


@frozen(kw_only=True)
class PkgDep:
    id: str


@frozen(kw_only=True)
class PkgLoggedVersion:
    version: str
    install_time: dt.datetime


@frozen(kw_only=True, eq=False)
class Pkg:
    source: str
    id: str
    slug: str
    name: str
    description: str
    url: str
    download_url: str
    date_published: dt.datetime
    version: str
    changelog_url: str
    options: PkgOptions  # pkg_options
    folders: list[PkgFolder]  # pkg_folder
    deps: list[PkgDep]  # pkg_dep

    def to_defn(self) -> Defn:
        return Defn(
            source=self.source,
            alias=self.slug,
            id=self.id,
            strategies=Strategies(
                asdict(  # pyright: ignore[reportArgumentType]
                    self.options,
                    value_serializer=lambda _, a, v: self.version
                    if a.name == Strategy.VersionEq and v is True
                    else v or None,
                )
            ),
        )
