#!/usr/bin/env python
# coding: UTF-8

import asyncio
from typing import List

import aiohttp
from bs4 import BeautifulSoup


async def attend(identifier: str, password: str) -> None:
    async with aiohttp.ClientSession() as session:
        data = dict(mb_id=identifier, mb_password=password)

        # login
        async with session.post('http://tcafe2a.com/bbs/login_check.php', data=data):
            pass

        # get hidden values
        async with session.get('http://www.tcafe2a.com/attendance/selfattend2.php') as res:
            attend_page = BeautifulSoup(await res.text(), features='html.parser')
            # language=JQuery-CSS
            hidden_values: List[BeautifulSoup] = attend_page.select('form[name=frm1] input[type=hidden]')

            data = {v.attrs['name']: v.attrs['value'] for v in hidden_values}

        # attend
        async with session.post('http://tcafe2a.com/attendance/selfattend2_p.php', data=data):
            pass


def main():
    asyncio.run(attend('', ''))


if __name__ == '__main__':
    main()
