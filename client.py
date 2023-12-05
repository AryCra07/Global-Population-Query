import asyncio

import aiohttp
import matplotlib.pyplot as plt

async def get_data(polygon):
    url = 'http://localhost:8848/data'
    data = {'coordinates': polygon}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            result = await response.json()
            return result['res'], result['total']

polygon = [[42441, 79189], [47339, 79189], [43231, 75803]]

res, total = asyncio.run(get_data(polygon))

x = [r[0] / 36000 for r in res]
y = [r[1] / 36000 for r in res]
z = [r[2] for r in res]

fig, ax = plt.subplots()
ax.scatter(x, y, c=z)

ax.set_title(f'Total Population: {total}')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

plt.show()