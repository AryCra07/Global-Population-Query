# Python程序设计-大作业

## 1.1 作业题目

### 1.1.1 数据

[`gpw-v4-population-count-rev11_2020_30_sec_asc.zip`](https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-count-rev11/data-download) 是一个全球人口分布数据压缩文件，解压后包括了8个主要的 `asc` 后缀文件，他们是全球网格化的人口分布数据文件，这些文件分别是：

- gpw-v4-population-count-rev11_2020_30_sec_1.asc
- gpw-v4-population-count-rev11_2020_30_sec_2.asc
- gpw-v4-population-count-rev11_2020_30_sec_3.asc

- gpw-v4-population-count-rev11_2020_30_sec_4.asc

- gpw-v4-population-count-rev11_2020_30_sec_5.asc

- gpw-v4-population-count-rev11_2020_30_sec_6.asc

- gpw-v4-population-count-rev11_2020_30_sec_7.asc

- gpw-v4-population-count-rev11_2020_30_sec_8.asc

这些文件分布对应地球不同经纬度的范围。

### 1.1.2 服务端

压缩文件（gpw-v4-population-count-rev11_2020_30_sec_asc.zip）是一个全球人口分布数据。基于 `Sanic` 实现一个查询服务，服务包括：

- 按给定的经纬度范围查询人口总数，查询结果采用 `JSON` 格式。

- 不可以采用数据库，只允许使用文件方式存储数据。

- 可以对现有数据进行整理以便加快查询速度，尽量提高查询速度。

- 查询参数格式 采用 [GeoJSON](https://geojson.org/) 的多边形（每次只需要查询一个多边形范围，只需要支持凸多边形）