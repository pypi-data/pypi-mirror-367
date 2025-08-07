from __future__ import annotations

from pathlib import Path

import pytest

from instawow.matchers.addon_toc import TocReader


@pytest.fixture
def fake_addon_toc(tmp_path: Path):
    fake_addon_path = tmp_path / 'FakeAddon' / 'FakeAddon.toc'
    fake_addon_path.parent.mkdir()
    fake_addon_path.write_text(
        """\
## Normal: Normal entry
##Compact:Compact entry
 ## Indented: Indented entry
# Comment:Not an entry

fake_addon.lua
""",
        encoding='utf-8',
    )
    return fake_addon_path


def test_loading_toc_from_path(fake_addon_toc: Path):
    TocReader.from_path(fake_addon_toc)
    with pytest.raises(FileNotFoundError):
        TocReader.from_path(fake_addon_toc.parent / 'MissingAddon.toc')


def test_parsing_toc_entries(fake_addon_toc: Path):
    toc_reader = TocReader.from_path(fake_addon_toc)
    assert dict(toc_reader) == {
        'Normal': 'Normal entry',
        'Compact': 'Compact entry',
    }


def test_toc_entry_indexing(fake_addon_toc: Path):
    toc_reader = TocReader.from_path(fake_addon_toc)
    assert toc_reader['Normal'] == 'Normal entry'
    assert toc_reader['Compact'] == 'Compact entry'
    assert toc_reader.get('Indented') is None
    assert toc_reader.get('Comment') is None
    assert toc_reader.get('Nonexistent') is None


def test_toc_interfaces():
    toc_reader = TocReader('')
    assert toc_reader.interfaces == []

    toc_reader = TocReader('## Interface: 10100')
    assert toc_reader.interfaces == [10100]

    toc_reader = TocReader('## Interface: 10100, 20200')
    assert toc_reader.interfaces == [10100, 20200]

    toc_reader = TocReader('## Interface:  10100 , 20200  ')
    assert toc_reader.interfaces == [10100, 20200]


def test_toc_version():
    toc_reader = TocReader('')
    assert toc_reader.version == ''

    toc_reader = TocReader('## Version: 1')
    assert toc_reader.version == '1'
