# coding: UTF-8
import os
from binascii import unhexlify
from collections.abc import Iterable

import aiohttp
import bs4
import pytest

from tcafe_attending_bot import _BASE_URL


@pytest.mark.asyncio
async def test_reachable() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(_BASE_URL) as res:
            print(res)


@pytest.mark.skipif(bool(os.getenv('ENABLE_SYNTHETIC', '')), reason='synthetic test disabled')
@pytest.mark.asyncio
async def test_synthetic() -> None:
    uid = os.getenv('TCAFE_ID')
    pwd = os.getenv('TCAFE_PWD')

    async with aiohttp.ClientSession(base_url=_BASE_URL) as session:
        data = dict(mb_id=uid, mb_password=pwd)

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

    assert 'secdoe' in data
    assert 'proctype' in data
    assert data['proctype'] == 'gogogo'
    assert len(unhexlify(data['secdoe'])) == 16
