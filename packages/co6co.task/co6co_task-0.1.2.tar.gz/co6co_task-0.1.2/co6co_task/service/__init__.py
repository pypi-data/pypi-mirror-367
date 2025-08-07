
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable
from co6co.utils.source import get_source_fun
from co6co.utils .singleton import Singleton
from typing import Tuple, Callable, Dict
from co6co.utils import log, try_except
'''
BlockingScheduler :     当调度器是你应用中唯一要运行的东西时
BackgroundScheduler :   当你没有运行任何其他框架并希望调度器在你应用的后台执行时使用（充电桩即使用此种方式）
AsyncIOScheduler :      当你的程序使用了asyncio（一个异步框架）的时候使用
GeventScheduler :       当你的程序使用了gevent（高性能的Python并发框架）的时候使用
TornadoScheduler :      当你的程序基于Tornado（一个web框架）的时候使用
TwistedScheduler :      当你的程序使用了Twisted（一个异步框架）的时候使用
QtScheduler :           如果你的应用是一个Qt应用的时候可以使用
'''


class CuntomCronTrigger(CronTrigger):
    """
    Cron 表达式解析器
    """
    # def __init__(self, year=None, month=None, day=None, week=None, day_of_week=None, hour=None,
    #              minute=None, second=None, start_date=None, end_date=None, timezone=None,
    #              jitter=None):
    #     super().__init__(year=None, month=None, day=None, week=None, day_of_week=None, hour=None,
    #              minute=None, second=None, start_date=None, end_date=None, timezone=None,
    #              jitter=None)
    @classmethod
    def resolvecron(cls, expr: str, timezone=None):
        """
        该解析使用6-7 corn 表达式 的解析,秒必填

        将 cron表达式 转换为 CronTrigger  
        在传统的 Unix/Linux Cron 表达式中 不包含 秒 即为 5-6 个字段 --> 分,时，天，月，星期，年[可选] 
        后加入了秒 变成 6-7 的 cron 表达式
        ┌──────────── [可选] 秒 (0 - 59)
        | ┌────────── 分钟 (0 - 59)
        | | ┌──────── 小时 (0 - 23)
        | | | ┌────── 天数 (1 - 31)
        | | | | ┌──── 月份 (1 - 12) OR jan,feb,mar,apr ...
        | | | | | ┌── 星期几 (0 - 6, 星期天 = 0) OR sun,mon ...
        | | | | | |
        * * * * * * 命令
        星号（*）：表示匹配任意值。例如，* 在分钟字段中表示每分钟都执行。
        逗号（,）：用于分隔多个值。例如，1,3,5 在小时字段中表示 1 点、3 点和 5 点执行。
        斜线（/）：用于指定间隔值。例如，*/5 在分钟字段中表示每 5 分钟执行一次。
        连字符（-）：用于指定范围。例如，10-20 在日期字段中表示从 10 号到 20 号。
        问号（?）：仅用于[日月周]字段，表示不指定具体值。通常用于避免冲突。
        weekday_mapping = {
            0: 'SUN',
            1: 'MON',
            2: 'TUE',
            3: 'WED',
            4: 'THU',
            5: 'FRI',
            6: 'SAT',
        }  
        """
        'SUN MON TUE WED THU FRI SAT',
        values = expr.split()
        if len(values) == 6:
            values.append(None)
        if len(values) != 7:
            raise ValueError('Wrong number of fields; got {}, expected 7,week:SUN MON TUE WED THU FRI SAT,不使用0-6的方式'.format(len(values)))
        return cls(second=values[0], minute=values[1], hour=values[2], day=values[3], month=values[4],
                   day_of_week=values[5], year=values[6], timezone=timezone)


class Scheduler(Singleton):
    _scheduler: BackgroundScheduler = None

    class Task:
        jobid: str = None
        stop: Callable[[], None] = None

        def __init__(self, jobid: str, stop: Callable[[], None]) -> None:
            self.jobid = jobid
            self.stop = stop

    def __init__(self) -> None:
        scheduler = BackgroundScheduler()

        # //todo 编译器解释 self._scheduler 为 Any 对象 为什么不是 BackgroundScheduler
        self._scheduler = scheduler
        self._scheduler.start()
        self._tasks: Dict[str, Scheduler.Task] = {}  # {key:str,jobid:str}
        pass

    @property
    def task_total(self) -> int:
        return len(self._tasks)

    @property
    def scheduler(self) -> BackgroundScheduler:
        return self._scheduler

    @staticmethod
    def parseCode(code: str) -> Tuple[bool,  Callable[[], any] | Exception]:
        try:
            main = get_source_fun(code, 'main')
            return True, main,
        except Exception as e:
            return False, e

    def exist(self, key: str) -> bool:
        """
        判断任务是否存在
        """
        return key in self._tasks

    def _getKey(self, jobid: str) -> str:
        """
        获取任务key
        """
        for key, value in self._tasks.items():
            if value.jobid == jobid:
                return key
        return None

    @try_except
    def getNextRun(self, key: str = None):
        # 获取所有作业
        jobs = self. scheduler.get_jobs()
        jobid = None
        data = []
        if key and key in self._tasks:
            jobid = self._tasks[key].jobid
        for job in jobs:
            if jobid and job.id != jobid:
                continue
            elif jobid:
                data.append({
                    "key": key,
                    "job_id": job.id,
                    "next_run_time": job.next_run_time,
                })
            else:
                key = self._getKey(job.id)
                data.append({
                    "key": key,
                    "job_id": job.id,
                    "next_run_time": job.next_run_time,
                })

        return data

    def removeTask(self, key: str):
        """
        移除任务
        """
        if key in self._tasks:
            task = self._tasks[key]
            self.scheduler.remove_job(task.jobid)
            if task.stop:
                task.stop()
            del self._tasks[key]
            return True
        else:
            log.info("任务{}不存在!!".format(key))
            return False

    def removeAll(self):
        self. scheduler.remove_all_jobs()
        for key, value in self._tasks.items():
            if value.stop:
                value.stop()
        self._tasks.clear()

    def stop(self):
        self.removeAll()
        self.scheduler.shutdown()

    def checkCode(self,  code: str, corn: str):
        """
        检查代码
        """
        try:
            res, _ = Scheduler.parseCode(code)
            if res:
                CuntomCronTrigger.resolvecron(corn)
                return True
            else:
                log.warn("解析代码失败：", code)
                return False
        except Exception as e:
            log.warn(f"解析corn:{code}失败")
            return False

    def addTask(self, key: str, code: str | Callable[[], None], corn: str, stop: Callable[[], None] = None):
        """
        增加任务
        """
        if key in self._tasks:
            msg = "任务'{}'已在运行!!".format(key)
            log.warn(msg)
            return False, msg
        try:
            trigger = CuntomCronTrigger.resolvecron(corn)
            scheduler: BackgroundScheduler = self._scheduler
            if isinstance(code, Callable):
                jobid = scheduler.add_job(code, trigger)
                self._tasks[key] = Scheduler.Task(jobid.id, stop)
                return True, ''
            res, main = Scheduler.parseCode(code)
            if res:
                jobid = scheduler.add_job(main, trigger)
                self._tasks[key] = Scheduler.Task(jobid.id, stop)
                return True, ''
            else:
                msg = "任务{}解析失败!!".format(key)
                log.warn("任务{}解析失败!!".format(key))
            return False, msg
        except Exception as e:
            msg = "任务{}发生错误:{}!!".format(key, e)
            log.err(msg)
            return False, msg

    def modifyTask(self, key: str, code: str | Callable[[], None], corn: str, stop: Callable[[], None] = None):
        """
        修改任务
        """
        if key in self._tasks:
            task = self._tasks[key]
            self.scheduler.remove_job(task.jobid)
            del self._tasks[key]
            self.addTask(key, code, corn, stop)
            return True
        else:
            log.info("任务{}不存在!!".format(key))
            return False


"""
def task(name):
    print('[{}]\t 执行时间:{}' . format(name, datetime.datetime.now()))


def startTimeTask(runTime: datetime.datetime = datetime.datetime.now()+datetime.timedelta(seconds=10)):
    #开始一个任务定时任务
    # scheduler调度器
    scheduler = BlockingScheduler()
    scheduler.add_job(task, 'date', run_date=runTime, args=['定时任务'], id='task')

    # scheduler.shutdown()
    scheduler.start()  # 阻塞


def startIntervalTask():
    #时间间隔任务
    scheduler = BlockingScheduler()
    scheduler.add_job(task, 'interval', seconds=10, args=["每隔10秒一次任"], id='task0')

    scheduler.add_job(task, 'cron', minute="*/2", args=["每隔2分钟一次任务"], id='task1')
    scheduler.start()


def cornTask():
    sc = BlockingScheduler()

    @sc.scheduled_job('cron', day_of_week='*', hour="*", minute='*', second='*/10', args=["cron注解任务10s一次任务"])
    def task(name):
        print('[{}]\t 执行时间:{}' . format(name, datetime.datetime.now()))
    sc.start()


def cornTask2():
    sc = BlockingScheduler()
    cronStart = "15 * * * * mon-fri *"
    sc.add_job(task, CuntomCronTrigger.resolvecron(cronStart), args=["cron注解任务10s一次任务"])
    sc.start()
"""
