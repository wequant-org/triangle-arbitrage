###############################################################
#   获取更多免费策略，请加入WeQuant比特币量化策略交流QQ群：519538535
#   WeQuant微宽网 - https://wequant.io
#   比特币量化交易/优质策略源码/精准回测/免费实盘，尽在微宽网 
###############################################################

三角套利使用文档：

1.程序组成：exchangeConnection文件夹包含3个市场交易接口，log文件夹存生成     	日志，utils文件夹包括一些公用函数，accountConfig.py包含账户信息配置， marketHelper.py 包含三个市场的封装好的统一接口， triangle_main.py是三角套利主程序。

2.使用说明：运行环境推荐：python3.6,安装requests包。首先accountConfig.py配置好access_key以及secret_key。然后在Triangle的__init__的方法里设定货币对（现在支持eth或者ltc或者etc作为base currency, btc作为quote currency, cny作为中间currency，进行三角套利），设定滑点和手续费，账户货币的保留数量，监控时间间隔（单位为秒），最小交易单位。 然后运行triangle_main.py

