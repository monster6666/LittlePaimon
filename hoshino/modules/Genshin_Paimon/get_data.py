from hoshino import aiorequests
from .util import get_headers, cache, get_use_cookie, get_own_cookie, check_retcode
from .db_util import update_cookie_cache
import datetime
import re
import random

# TODO：注意每处参数顺序的更改
@cache(ttl=datetime.timedelta(hours=1))
async def get_abyss_data(user_id, uid, schedule_type = "1", use_cache=True):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    url ="https://api-takumi.mihoyo.com/game_record/app/genshin/api/spiralAbyss"
    params ={
        "schedule_type": schedule_type,
        "role_id": uid,
        "server": server_id}
    while True:
        cookie = await get_use_cookie(user_id, uid=uid, action='查询深渊')
        if not cookie:
            return '现在派蒙没有可以用的cookie哦，可能是:\n1.公共cookie全都达到了每日30次上限\n2.公共池全都失效了或没有cookie\n让管理员使用 添加公共ck 吧!'
        headers = get_headers(q=f'role_id={uid}&schedule_type={schedule_type}&server={server_id}', cookie=cookie['cookie'])
        res = await aiorequests.get(url=url, headers=headers, params=params)
        data = await res.json()
        if await check_retcode(data, cookie, uid):
            return data
        

async def get_daily_note_data(uid):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    url ="https://api-takumi.mihoyo.com/game_record/app/genshin/api/dailyNote"
    cookie = await get_own_cookie(uid, action='查询实时便签')
    if not cookie:
            return f'你的uid{uid}没有绑定对应的cookie,使用ysb绑定才能用实时便签哦!'
    await update_cookie_cache(cookie['cookie'], uid, 'uid')
    headers = get_headers(q=f'role_id={uid}&server={server_id}', cookie=cookie['cookie'])
    params = {
        "server": server_id,
        "role_id": uid
    }
    res = await aiorequests.get(url=url, headers=headers, params=params)
    return await res.json()

@cache(ttl=datetime.timedelta(hours=1))
async def get_player_card_data(user_id, uid, use_cache=True):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    url ="https://api-takumi.mihoyo.com/game_record/app/genshin/api/index"
    params = {
        "server": server_id,
        "role_id": uid
    }
    while True:
        cookie = await get_use_cookie(user_id, uid=uid, action='查询原神卡片')
        if not cookie:
            return '现在派蒙没有可以用的cookie哦，可能是:\n1.公共cookie全都达到了每日30次上限\n2.公共池全都失效了或没有cookie\n让管理员使用 添加公共ck 吧!'
        headers = get_headers(q=f'role_id={uid}&server={server_id}', cookie=cookie['cookie'])
        res = await aiorequests.get(url=url, headers=headers, params=params)
        data =  await res.json()
        if await check_retcode(data, cookie, uid):
            return data

@cache(ttl=datetime.timedelta(hours=1))
async def get_chara_detail_data(user_id, uid, use_cache=True):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    json_data = {
        "server": server_id,
        "role_id": uid,
        "character_ids": []
    }
    url = 'https://api-takumi.mihoyo.com/game_record/app/genshin/api/character'
    while True:
        cookie = await get_use_cookie(user_id, uid=uid, action='查询角色详情')
        if not cookie:
            return '现在派蒙没有可以用的cookie哦，可能是:\n1.公共cookie全都达到了每日30次上限\n2.公共池全都失效了或没有cookie\n让管理员使用 添加公共ck 吧!'
        headers = get_headers(b=json_data, cookie=cookie['cookie'])
        res = await aiorequests.post(url=url, headers=headers, json=json_data)
        data =  await res.json()
        if await check_retcode(data, cookie, uid):
            return data

@cache(ttl=datetime.timedelta(hours=1))
async def get_chara_skill_data(uid, chara_id, use_cache=True):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    url = 'https://api-takumi.mihoyo.com/event/e20200928calculate/v1/sync/avatar/detail'
    cookie = await get_own_cookie(uid, action='查询角色天赋')
    if not cookie:
        return None
    await update_cookie_cache(cookie['cookie'], uid, 'uid')
    headers = get_headers(q=f'uid={uid}&region={server_id}&avatar_id={chara_id}', cookie=cookie['cookie'])
    params = {
        "region": server_id,
        "uid": uid,
        "avatar_id": chara_id
    }
    res = await aiorequests.get(url=url, headers=headers, params=params)
    data =  await res.json()
    # TODO:待定，未知cookie对技能的影响
    return data

@cache(ttl=datetime.timedelta(hours=1))
async def get_monthinfo_data(uid, month, use_cache=True):
    server_id = "cn_qd01" if uid[0] == '5' else "cn_gf01"
    url = 'https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo'
    cookie = await get_own_cookie(uid, action='查询每月札记')
    if not cookie:
        return f'你的uid{uid}没有绑定对应的cookie,使用ysb绑定才能用每月札记哦!'
    await update_cookie_cache(cookie['cookie'], uid, 'uid')
    headers = get_headers(q=f'month={month}&bind_uid={uid}&bind_region={server_id}', cookie=cookie['cookie'])
    params = {
        "month": int(month),
        "bind_uid": uid,
        "bind_region": server_id
    }
    res = await aiorequests.get(url=url, headers=headers, params=params)
    data =  await res.json()
    if await check_retcode(data, cookie, uid):
        return data

async def get_bind_game(cookie):
    finduid = re.search(r'account_id=(\d{6,12})', cookie)
    if not finduid:
        return None
    uid = finduid.group(1)
    url = 'https://api-takumi.mihoyo.com/game_record/card/wapi/getGameRecordCard'
    headers = get_headers(q=f'uid={uid}', cookie = cookie)
    params = {
        "uid": uid
    }
    res = await aiorequests.get(url=url, headers=headers, params=params)
    return (await res.json()), uid



    