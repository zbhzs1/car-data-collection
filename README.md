# 公开汽车信息采集与数据处理

面向汽车公开信息的采集与结构化处理工具，完成网页字段解析、数据清洗、质量校验、SQLite 入库以及 CSV/Excel 导出。项目不登录、不绕过验证码、不采集个人敏感信息。

## 运行

```bash
pip install -r requirements.txt
python scraper.py --html path/to/page.html --output outputs
```

运行后会生成原始数据、清洗结果、Excel文件、SQLite数据库和运行日志。

脚本也支持公开静态页面：

```bash
python scraper.py --url "https://example.com/public-cars" --output outputs
```

使用公开网站前，应先确认网站的访问条款和 robots 规则，并控制请求频率。

## 数据处理流程

原始HTML → CSS选择器解析 → 字段标准化 → 重复/缺失/异常检查 → SQLite/CSV/Excel。

项目重点包括 Requests/BeautifulSoup/Pandas 采集与处理、字段字典、数据质量规则、失败重试、日志记录和结果导出。

## 公开API采集

`nhtsa_crawl.py` 使用 NHTSA vPIC 公开接口采集真实的乘用车品牌数据，记录原始JSON、清洗结果、抓取时间和来源URL；运行方式：

```bash
python nhtsa_crawl.py
```
