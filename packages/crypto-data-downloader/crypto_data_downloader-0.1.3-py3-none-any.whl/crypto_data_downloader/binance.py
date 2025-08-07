import asyncio
import os
from typing import Dict, List, Union

import numpy as np
from aiohttp import ClientSession

from .utils import (
    TO_MS,
    encode_query,
    load_pkl,
    parse_date,
    save_json,
    save_pkl,
    split_intervals,
    timestamp,
)

WEIGHTS = {
    "/api/v3/time": 1,
    "/api/v3/exchangeInfo": 20,
    "/api/v3/klines": 2,
}


ALL_COLUMNS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "n_trades",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
    "unused",
]


class CryptoDataDownloader:
    base = "https://api.binance.com"
    info_path = "data/info.json"
    weight_key = "x-mbx-used-weight-1m"

    weight_lim = 5000
    quote = "USDT"
    interval = "5m"
    kline_lim = 1000
    columns = ["open_time", "close"]

    async def get(s, url: str):
        # assert urlparse(url).path in WEIGHTS, url
        if not hasattr(s, "ses"):
            s.ses = ClientSession()
        async with s.ses.get(url) as r:
            if s.weight_key in r.headers:
                s.weight_used = int(r.headers[s.weight_key])
            return await r.json()

    async def get_time_n_weight(s):
        url = f"{s.base}/api/v3/time"
        r = await s.get(url)
        t_server = r["serverTime"]
        t_my = timestamp()
        s.t_diff = t_server - t_my
        print(
            f"server time: {t_server}, my time: {t_my}, diff: {s.t_diff} ms, weight used: {s.weight_used}"
        )

    async def get_info(s):
        url = f"{s.base}/api/v3/exchangeInfo"
        s.info = await s.get(url)
        save_json(s.info, s.info_path)

        r = next(
            x for x in s.info["rateLimits"] if x["rateLimitType"] == "REQUEST_WEIGHT"
        )
        s.weight_lim = min(s.weight_lim, r["limit"])

        symbols = [x for x in s.info["symbols"] if x["quoteAsset"] == s.quote]
        for x in symbols:
            x["permissions"] = sum(x["permissionSets"], start=[])
        spot = [x for x in symbols if "SPOT" in x["permissions"]]
        margin = [x for x in symbols if "MARGIN" in x["permissions"]]
        print(
            f"weight lim: {s.weight_lim}/{r['limit']}, {s.quote} symbols: {len(symbols)}, spot: {len(spot)}, margin: {len(margin)}"
        )
        s.symbols = symbols

    async def get_kline(s, query: Dict):
        query.update(dict(interval=s.interval, limit=s.kline_lim))
        url = f"{s.base}/api/v3/klines?{encode_query(query)}"
        r = await s.get(url)
        if len(r) == 0:
            return r
        indices = [ALL_COLUMNS.index(x) for x in s.columns]
        return np.array(r, float)[:, indices]

    async def download(s, start, end):
        data_path = f"data/crypto_data_{start}_{end}.pkl"
        raw_path = f"data/raw_crypto_data_{start}_{end}.pkl"
        await s.get_info()

        start, end = parse_date(start), parse_date(end)
        a, b = int(s.interval[:-1]), s.interval[-1]
        dt = int(s.kline_lim * a * TO_MS[b])
        intervals = split_intervals(start, end, dt)
        n_req = len(intervals) * len(s.symbols)
        weight = WEIGHTS["/api/v3/klines"]
        n_mins = n_req * weight / s.weight_lim
        print(
            f"{len(intervals)} intervals * {len(s.symbols)} symbols = {n_req} requests -> {n_mins} minutes"
        )

        if os.path.exists(raw_path):
            s.data = load_pkl(raw_path)
        else:
            s.data = []
            for x in s.symbols:
                sym = x["symbol"]
                s.data += [
                    dict(query=dict(symbol=sym, startTime=a, endTime=b), res=None)
                    for a, b in intervals
                ]

        while True:
            left = [x for x in s.data if x["res"] is None]
            print(f"left: {len(left)}/{len(s.data)}")
            if len(left) == 0:
                break
            await s.get_time_n_weight()
            num = (s.weight_lim - s.weight_used) // weight

            async def get_one(x):
                try:
                    x["res"] = await s.get_kline(x["query"])
                except Exception as e:
                    s.errors.append(f"{x['query']} -> {e}")

            s.errors = []
            await asyncio.gather(*[get_one(x) for x in left[:num]])
            save_pkl(s.data, raw_path)
            if len(s.errors):
                save_json(s.errors, "data/errors.json")
            await asyncio.sleep(60)

        data2: Dict[str, Union[np.ndarray, List[np.ndarray]]] = {}
        for x in s.data:
            sym = x["query"]["symbol"]
            if sym not in data2:
                data2[sym] = []
            if len(x["res"]):
                data2[sym].append(x["res"])
        for sym, arrays in list(data2.items()):
            # print(sym, [f"{format_date(x[0, 0])} {format_date(x[-1, 0])}" for x in arrays])
            if len(arrays):
                data2[sym] = np.concatenate(arrays)
                # print(sym, data2[sym].shape)
            else:
                del data2[sym]
        save_pkl(data2, data_path, gz=True)

        if hasattr(s, "ses"):
            await s.ses.close()
