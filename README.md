# victor-algo-trading-v1
 For v1, build a good monitor dashboard and develop a strategy building class.

运行所需api和key：
1. Kaiko Api Key
2. Fred Api Key (免费注册)
3. Influxdb Token

数据源：
1. crypto: Kaiko
2. macro: Fred
3. forex & commodity: Yahoo Finance
4. news: Google News ????
5. Rapid API （目前没打算用，可能之后搜集每日的数据的时候用到）
6. 

目标：
在GCP上存储数据（动态数据，目前打算存储coinmarketcap上前10名的coin在最大的几家交易所上的trade和ohlcv等数据）
同时直接GCP上跑模型和algo策略，然后上传influxdb（host在GCP上）上，然后用grafana展示，展示的还有策略的收益买卖点等

数据源：kaiko，我自己的api

建立本地数据库！


计划：
1. 既然我要经常update代码，不如把logging存到gcp上
2. 对于live的数据，添加使用rest api获取历史数据的过程！
3. 在所有call api的时候，都要添加try然后在里面加入如果失败则再跑一次，最多3次（或者n次，在variable里记录） 
4. Daily更新的数据，很多其实并不在同一时间更新，但是我目前是每三个小时更新一次数据
5. grafana里面添加报警系统，或者在代码里，绑定微信，或者发送邮件
6. 添加新闻大事件的数据，比如美联储会议，美国大选等日期，然后在grafana里面添加一个新闻大事件的图表
7. 之后在上传数据的时候，只上传最后一天的！省一下influxdb的resource！
8. 用google trend找一些近期的热门词，然后在grafana里面添加一个热门词的图表
9. 爬虫，之后，用chatgpt来判断新闻的情感，然后在grafana里面添加一个情感的图表
10. 继续找CDS数据，在grafana中显示前几名的，或者等
11. （非重要）添加财报数据，并画图，加上行业，可以filter对比，然后添加造假很可能的一些指标 - 参考https://pypi.org/project/yahoofinancials/
12. 外汇数据里面，添加一些常用的套利的走势，比如eur/usd和eur/jpy的走势，然后在grafana里面添加一个套利的图表
13. kaiko data里面加入ohlcv，和volume什么的，加上slippage图，加上orderbook的density相关的
14. 大宗商品
15. 找找那种比如拖拉机销量什么的数据，monthly quarterly就行，然后做个预测
16. 专门搞个dashboard，里面放上预测，然后到日期后与实际数据对比
17. 把每一个数据的availability全部放到一个专门的bucket里面，然后在dashboard首页放一下，告知自己或者别人
18. 自动在云端处理数据，挑出那些有异常值的，然后用一个柱状图等类似的展示，0和1，和2。比如银行危机的时候金价大涨，或者可以把这些东西罗列出来
19. 添加crypto的orderbook data
20. 


说明：
1. 关于日志的话，每一种数据都有各自的日志，存储在logging文件夹里
2. 所有的时间，都以UTC时间基准
3. influxDB里面，measurement名字中，IR_CB代表interest rate, corporate bond
4. Availability check中，0是获取数据的代码没有运行，压根没有尝试获取数据，-1是获取失败，1是数据available


Bug解决：
1. 添加方案，如果stream没有数据，用rest获取，然后加入本地数据库
2. （不太重要）对于每日或者隔几天更新的数据，历史数据因为是0:0:0，所以转换成UTC的时候会变成1点
3. OB data的话，我大概率在influxdb上会设置30天，数据量实在太大了。。。


宏观数据更新时间
1. Corporate Bond: Every day update yesterday's data, at 4pm Paris time (10am New York time) - according to Fred website
2. Moody's Seasoned Aaa Baa Corporate Bond Yield: Every day
3. 