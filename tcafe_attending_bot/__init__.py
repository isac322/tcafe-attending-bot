"""Auto attending bot for TCafe."""

from __future__ import annotations

import asyncio
import json
import logging
import pathlib
from collections.abc import Iterable, Generator
from itertools import chain
from typing import Final

import aiohttp
import bs4
import xdg_base_dirs

__version__ = '1.0.0'

_log: Final[logging.Logger] = logging.getLogger(__name__)
_BASE_URL: Final[str] = 'https://tcafe2a.com'
_APP_NAME: Final[str] = 'tcafe'


async def attend(identifier: str, password: str) -> None:
    _log.info(f'Processing {identifier}...')

    try:
        async with aiohttp.ClientSession(base_url=_BASE_URL) as session:
            data = dict(mb_id=identifier, mb_password=password)

            # login
            async with session.post('/bbs/login_check.php', data=data) as res:
                if not res.ok:
                    raise ValueError('Failed to log in')

                result_page = bs4.BeautifulSoup(await res.text(), features='html.parser')
                title = result_page.select_one('title')
                if '오류' in title.text:
                    raise ValueError('Failed to log in')

            # get hidden values
            async with session.get('/community/attendance') as res:
                if not res.ok:
                    raise ValueError('Failed to get attendance page')

                attend_page = bs4.BeautifulSoup(await res.text(), features='html.parser')
                # language=JQuery-CSS
                hidden_values: Iterable[bs4.Tag] = attend_page.select('form[name=frm1] input[type=hidden]')

                data = {v.attrs['name']: v.attrs['value'] for v in hidden_values}
                _log.info(data)

            # attend
            async with session.post('/attendance/selfattend2_p.php', data=data):
                if not res.ok:
                    raise ValueError('Failed to attend')
    except IOError:
        _log.exception(f'Fail to attend {identifier}')
    else:
        _log.info(f'{identifier} is attended!')


def _get_accounts() -> Generator[tuple[str, str], None, None]:
    for directory in chain(xdg_base_dirs.xdg_data_dirs(), (xdg_base_dirs.xdg_data_home(),)):
        config_path = pathlib.Path(directory) / _APP_NAME / 'accounts.json'

        if not config_path.is_file():
            continue

        try:
            with config_path.open() as fp:
                config = json.load(fp)
        except IOError:
            _log.exception(f'Fail to read account info from {config_path}')
            continue

        if not isinstance(config, list):
            continue

        for account in config:
            if (
                not isinstance(account, dict)
                or not isinstance(account.get('id'), str)
                or not isinstance(account.get('password'), str)
            ):
                continue

            yield account['id'], account['password']


async def run() -> None:
    _log.addHandler(logging.StreamHandler())
    _log.setLevel(logging.INFO)

    results = await asyncio.gather(*(attend(_id, _pw) for _id, _pw in _get_accounts()))
    if len(results) == 0:
        raise ValueError('Empty accounts')


def main() -> None:
    asyncio.run(run())
