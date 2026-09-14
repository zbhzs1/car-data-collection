# 公开汽车信息采集与数据处理

这是一个可运行的个人项目：对公开网页中的车型卡片进行采集，完成字段解析、清洗、SQLite 入库和 CSV/Excel 导出。项目仅使用公开页面或本地示例页面，不登录、不绕过验证码、不采集个人敏感信息。

## 运行

```bash
pip install -r requirements.txt
python scraper.py --html fixtures/cars.html --output outputs
```

运行后会生成 `outputs/cars_raw.csv`、`outputs/cars_clean.csv`、`outputs/cars.xlsx`、`outputs/cars.db` 和 `outputs/run.log`。

脚本也支持公开静态页面：

```bash
python scraper.py --url "https://example.com/public-cars" --output outputs
```

使用真实网站前，应先确认网站的公开访问条款和 robots 规则，并控制请求频率。

## 数据流程

原始HTML → CSS选择器解析 → 字段标准化 → 重复/缺失/异常检查 → SQLite/CSV/Excel。

## 面试可说明

项目重点是 Requests/BeautifulSoup/Pandas 的基础采集、字段字典、数据质量规则、失败重试、日志记录和结果导出；默认示例数据为本地公开格式样例，不是企业内部数据。
