# victor-algo-trading-v1
 For v1, build a good monitor dashboard and develop a strategy building class.

目标：
在GCP上存储数据（动态数据，目前打算存储coinmarketcap上前10名的coin在最大的几家交易所上的trade和ohlcv等数据）
同时直接GCP上跑模型和algo策略，然后上传influxdb（host在GCP上）上，然后用grafana展示，展示的还有策略的收益买卖点等

数据源：kaiko，我自己的api

建立本地数据库！


计划：
1. 既然我要经常update代码，不如把logging存到gcp上
2. 对于live的数据，添加使用rest api获取历史数据的过程！
3. 在所有call api的时候，都要添加try然后在里面加入如果失败则再跑一次，最多3次（或者n次，在variable里记录）


说明：
1. 关于日志的话，每一种数据都有各自的日志，存储在logging文件夹里
2. 所有的时间，都以UTC时间基准
3. 

Bug解决：
1. 添加方案，如果stream没有数据，用rest获取，然后加入本地数据库
2. （不太重要）对于每日或者隔几天更新的数据，历史数据因为是0:0:0，所以转换成UTC的时候会变成1点


宏观数据更新时间
1. Corporate Bond: Every day update yesterday's data, at 4pm Paris time (10am New York time) - according to Fred website
2. Moody's Seasoned Aaa Baa Corporate Bond Yield: Every day
3. 