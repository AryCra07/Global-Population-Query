#  server.py
#  Copyright (c) 2023 Yuanhao Shen

import asyncio
import math
import numpy as np
from sanic import Sanic
from sanic.response import json
from sanic.log import logger
from shapely.geometry import Polygon
from shapely.errors import TopologicalError
from pre_processor import preprocess

app = Sanic("population")


@app.listener('before_server_start')
async def setup(app, loop):
    await preprocess()


async def get_block_data(block_x, block_y, polygon, step):
    logger.info(f"Query on block x: {block_x} y: {block_y}")
    res = []
    total = 0
    min_x, min_y, max_x, max_y = polygon.bounds
    block_data = np.load(f"./data/data_{block_x}_{block_y}.npy")
    for second_x in range(max(block_x * 3600, math.floor(min_x / 30) * 30),
                          min((block_x + step) * 3600, math.ceil(max_x / 30) * 30), 30):
        for second_y in range(min(block_y * 3600, math.ceil(max_y / 30) * 30),
                              max((block_y - step) * 3600, math.floor(min_y / 30) * 30), -30):
            x_offset = int((block_y * 3600 - second_y) / 30)
            y_offset = int((second_x - block_x * 3600) / 30)
            cell_polygon = Polygon(((second_x, second_y), (second_x + 30, second_y), (second_x + 30, second_y - 30),
                                    (second_x, second_y - 30))).intersection(polygon)
            if cell_polygon.area > 0:
                res.append((second_x, second_y, cell_polygon.area / 900 * block_data[x_offset, y_offset]))
                if not np.isnan(res[-1][2]):
                    total += res[-1][2]
    return res, total


@app.post("/data")
async def get_data(request):
    """
    data接口，接受一个多边形的坐标列表，返回该多边形内的人口数据
    :param request: 格式为{"coordinates": [[x1, y1], [x2, y2], ...]}
    :return: 格式为{"total": 人口总数, "res": [[x1, y1, 人口数], [x2, y2, 人口数], ...]}
    """
    try:
        point_list = request.json.get("coordinates")
        polygon = Polygon(point_list)  # 构造多边形
        logger.info(f"Query prarms: {point_list}")
        min_x, min_y, max_x, max_y = polygon.bounds
        step = 10  # 一个block跨10度
        res = []
        total = 0
        task_list = []
        for block_x in range(math.floor(min_x / 3600 / step) * step, math.ceil(max_x / 3600 / step) * step, step):
            for block_y in range(math.ceil(max_y / 3600 / step) * step, math.floor(min_y / 3600 / step) * step, -step):
                task_list.append(
                    asyncio.create_task(get_block_data(block_x, block_y, polygon, step)))  # 每个block中的查询并行处理
        for task in task_list:
            res_, total_ = await task
            res += res_
            total += total_
        return json({"total": total, "res": res})
    except KeyError:  # 参数错误
        return json([], status=400)
    except (ValueError, TopologicalError):  # 非多边形
        return json([], status=406)


if __name__ == '__main__':
    app.run(port=8848)