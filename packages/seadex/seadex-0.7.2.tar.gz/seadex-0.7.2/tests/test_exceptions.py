from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from seadex import EntryNotFoundError, EntryRecord, SeaDexEntry

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


def test_entry_record_no_expand_trs() -> None:
    msg = (
        "The provided data does not contain the 'trs' key in the 'expand' field. "
        "If you got this data from the SeaDex API, "
        "it means that you didn't add `expand=trs` to your query parameters."
    )
    with pytest.raises(ValueError, match=msg):
        EntryRecord.from_dict({})


def test_entry_not_found_from_anilist_id(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://releases.moe/api/collections/entries/records?perPage=500&expand=trs&filter=alID%3D98329837198378237183918&skipTotal=true",
        json={"page": 1, "perPage": 30, "totalItems": 0, "totalPages": 0, "items": []},
    )

    with pytest.raises(EntryNotFoundError):
        with SeaDexEntry() as seadex_entry:
            seadex_entry.from_id(98329837198378237183918)


def test_entry_not_found_from_seadex_id(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://releases.moe/api/collections/entries/records?perPage=500&expand=trs&filter=id%3D%27jashdsjhdsakjdhsakdhsadhaksjd%27&skipTotal=true",
        json={"page": 1, "perPage": 30, "totalItems": 0, "totalPages": 0, "items": []},
    )

    with pytest.raises(EntryNotFoundError):
        with SeaDexEntry() as seadex_entry:
            seadex_entry.from_id("jashdsjhdsakjdhsakdhsadhaksjd")


def test_entry_not_found_from_title(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://graphql.anilist.co",
        json={
            "errors": [{"message": "Not Found.", "status": 404, "locations": [{"line": 1, "column": 28}]}],
            "data": {"Media": None},
        },
    )

    with pytest.raises(EntryNotFoundError):
        with SeaDexEntry() as seadex_entry:
            seadex_entry.from_title("jashdsjhdsakjdhsakdhsadhaksjd")


def test_from_filter_invalid_type() -> None:
    with pytest.raises(TypeError, match="'filter' must be a string, not object."):
        with SeaDexEntry() as seadex_entry:
            next(seadex_entry.from_filter(object()))  # type: ignore[arg-type]


def test_from_infohash_type() -> None:
    with pytest.raises(TypeError, match="'infohash' must be a string, not object."):
        with SeaDexEntry() as seadex_entry:
            next(seadex_entry.from_infohash(object()))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "infohash",
    ["certainly not a infohash", "2120e6faea8860ffa07bf535ea89a150b4fda773a", "2120e6faea8860ffa07bf535ea89a150b4fda7"],
)
def test_from_infohash_format(infohash: str) -> None:
    with pytest.raises(ValueError, match="Invalid infohash format. Must be a 40-character hexadecimal string."):
        with SeaDexEntry() as seadex_entry:
            next(seadex_entry.from_infohash(infohash))
