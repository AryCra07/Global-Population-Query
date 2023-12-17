import os
import numpy as np


def preprocess():
    """
    预处理数据，将原始数据处理成10度*10度的block
    """
    for i in range(1, 9):
        step = 10  # 处理成10度*10度的block
        with open(f"./gpw-v4-population-count-rev11_2020_30_sec_asc/gpw_v4_population_count_rev11_2020_30_sec_{i}.asc",
                  "r") as f:
            f.readline()
            f.readline()
            stx = int(float(f.readline().split()[1]))  # 左上角经度
            sty = int(float(f.readline().split()[1])) + 90  # 左上角纬度
            cooked = True  # 该部分中的所有block是否已经被处理
            for x_offset in range(0, 90, step):
                for y_offset in range(0, 90, step):
                    if not os.path.exists(f"./data/data_{stx + x_offset}_{sty - y_offset}.npy"):
                        cooked = False
        print(f"Processing data on x: {stx} y: {sty}")
        if cooked:
            continue
        data = np.genfromtxt(
            f"./gpw-v4-population-count-rev11_2020_30_sec_asc/gpw_v4_population_count_rev11_2020_30_sec_{i}.asc",
            skip_header=6)
        data[data == -9999] = np.nan  # 空数据
        for x_offset in range(0, 90, step):
            for y_offset in range(0, 90, step):
                if not os.path.exists(f"./data/data_{stx + x_offset}_{sty - y_offset}.npy"):
                    print(f"Creating data_{stx + x_offset}_{sty - y_offset}.npy")
                    np.save(f"./data/data_{stx + x_offset}_{sty - y_offset}.npy",
                            data[y_offset * 120:(y_offset + step) * 120, x_offset * 120:(x_offset + step) * 120])


if __name__ == '__main__':
    preprocess()
