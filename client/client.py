import tkinter as tk
from tkinter import messagebox
import requests
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from PIL import Image, ImageTk


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"[{self.x},{self.y}]"

    @property
    def x_deg(self):
        return self.x // 3600

    @property
    def x_min(self):
        return self.x % 3600 // 60

    @property
    def x_sec(self):
        return self.x % 60

    @property
    def y_deg(self):
        return self.y // 3600

    @property
    def y_min(self):
        return self.y % 3600 // 60

    @property
    def y_sec(self):
        return self.y % 60


class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("全球人口分布查询")
        self.coordinate_list = []
        self.setup_ui()

    def setup_ui(self):
        # 设置图像显示区域
        self.canvas = tk.Canvas(self.root, width=1400, height=700)
        self.canvas.pack(side="left")

        self.load_world_map()

        # 设置列表显示区域
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(side="right", fill="both", expand=True)

        self.listbox = tk.Listbox(self.list_frame)
        self.listbox.pack(side="top", fill="both", expand=True)

        self.submit_button = tk.Button(self.list_frame, text="提交", command=self.submit)
        self.submit_button.pack(side="bottom")

        # 删除按钮
        self.remove_button = tk.Button(self.list_frame, text="删除最近坐标", command=self.remove_last_point)
        self.remove_button.pack(side="bottom")

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def load_world_map(self):
        try:
            # 加载图片并调整大小以适合 Canvas
            self.map_image = Image.open('D:\ASchool\大三上\【5】Python\MyH\Final\Population\client\world_map_gridded.png')
            self.map_image = self.map_image.resize((1400, 700), Image.Resampling.LANCZOS)  # 修改这里
            self.map_photo = ImageTk.PhotoImage(self.map_image)

            # 在 Canvas 上绘制图片
            self.canvas.create_image(0, 0, anchor="nw", image=self.map_photo)
        except IOError:
            print("无法加载地图图片")

    def on_canvas_click(self, event):
        x = event.x / self.canvas.winfo_width() * 1296000 - 648000
        y = -(event.y / self.canvas.winfo_height() * 648000 - 324000)
        self.add_point(x, y)

    def add_point(self, x, y):
        self.coordinate_list.append(Coordinate(x, y))
        self.update_listbox()

    def remove_last_point(self):
        if self.coordinate_list:
            self.coordinate_list.pop()
            self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for coord in self.coordinate_list:
            self.listbox.insert(tk.END,
                                f"{coord.x_deg}°{coord.x_min}′{coord.x_sec}″, {coord.y_deg}°{coord.y_min}′{coord.y_sec}″")

    def submit(self):
        if not self.coordinate_list:
            messagebox.showinfo("提示", "列表为空，请先添加坐标点！")
            return

        # 准备请求数据
        coordinates = [[coord.x, coord.y] for coord in self.coordinate_list]
        payload = {
            "type": "Polygon",
            "coordinates": coordinates
        }

        try:
            r = requests.post("http://127.0.0.1:8848/data", json=payload)
            if r.status_code != 200:
                messagebox.showerror("错误", f"服务器返回错误: {r.status_code}")
                return

            # 解析返回的数据
            response_data = r.json()
            data = np.array(response_data.get("res")).transpose((1, 0))
            total_population = response_data.get("total")

            # 使用 Matplotlib 和 Cartopy 绘制结果
            self.plot_result(data, total_population)
        except requests.RequestException as e:
            messagebox.showerror("错误", f"请求失败: {e}")

    def plot_result(self, data, total_population):
        extent = [np.min(data[0]) / 3600, np.max(data[0]) / 3600,
                  np.min(data[1]) / 3600, np.max(data[1]) / 3600]
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        ax.set_extent(extent, crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.LAND.with_scale('10m'))  # 图背景的陆地标识
        ax.add_feature(cfeature.COASTLINE.with_scale('10m'), lw=0.25)  # 图背景的海岸线标识
        ax.add_feature(cfeature.OCEAN.with_scale('10m'))  # 图背景的海洋标识
        ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
        im = ax.scatter(data[0] / 3600, data[1] / 3600, s=0.5, c=data[2], cmap='viridis', vmin=0, vmax=500)
        fig.colorbar(im, ax=ax)
        ax.title.set_text(f"Total population of the area is {total_population:.2f}")
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
