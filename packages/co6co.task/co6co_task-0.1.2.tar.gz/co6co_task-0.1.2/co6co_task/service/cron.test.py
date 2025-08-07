import datetime
from ..croniter import croniter


# cron 表达式
# 秒、分、小时、日期、月份、周几（有些系统支持）、年份（可选）
cron_exp = "0 0 * * MON-FRI"

# 创建 croniter 对象
cron = croniter(cron_exp,  datetime.datetime.now())

# 获取下一次满足条件的时间
next_time = cron.get_next(datetime.datetime)
print("Next scheduled time:", next_time)
