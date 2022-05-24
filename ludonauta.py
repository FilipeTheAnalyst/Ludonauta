import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
from time import perf_counter


async def get_page(session, url):
    async with session.get(url) as r:
        return await r.text()


async def get_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(get_page(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results


async def main(urls):
    async with aiohttp.ClientSession() as session:
        data = await get_all(session, urls)
        return data


def parse(results):
    df = pd.DataFrame()
    names = []
    num_players = []
    playing_time = []
    players = re.compile(r"\d*-*\d*")
    min_age = []

    for html in results:
        soup = bs(html, 'html.parser')
        for game in soup.find_all(class_='product-desc m-n'):
            names.append(game.find(class_='product-name').text.strip())
            num_players.append(re.search(players,
                                         game.find('span', {'title': 'Núm. jugadores'}).text.strip()).group())
            try:
                playing_time.append(re.search(players,
                                              game.find('span', {'title': 'Tiempo juego'}).text.strip()).group())
            except:
                playing_time.append('N/A')
            try:
                min_age.append(re.search(players,
                                         game.find('span', {'title': 'Edad mínima'}).text.strip()).group())
            except:
                min_age.append('N/A')

    df = pd.DataFrame(
        data={"name": names, "num_players": num_players, "play_time": playing_time, "min_age": min_age})
    return df


if __name__ == '__main__':
    urls = [
        'https://www.ludonauta.es/juegos-mesas-tiendas/listar-por-tienda/dracotienda/page:1',
        'https://www.ludonauta.es/juegos-mesas-tiendas/listar-por-tienda/dracotienda/page:2',
        'https://www.ludonauta.es/juegos-mesas-tiendas/listar-por-tienda/dracotienda/page:3'
    ]
    start = perf_counter()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(main(urls))
    print(parse(results))
    stop = perf_counter()
    print("time taken:", stop - start)
