import uvicorn
from loguru import logger
from app.config import config
from pathlib import Path
import threading
import time
import functools

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.jobstores.memory import MemoryJobStore
from app.deep_learning.tsmixer import get_training_data

# 全局变量
LOCK_FILE_PATH = Path(__file__).parent.joinpath('assets/runtime/file_lock.lock')
job_status = {}
stop_event = threading.Event()
stop_loss_process = None

def log_job_execution(event):
    if event.exception:
        logger.error(f"作业 {event.job_id} 执行失败: {event.exception}")
        job_status[event.job_id] = {'status': 'failed', 'last_run': event.scheduled_run_time}
    else:
        logger.info(f"作业 {event.job_id} 执行成功")
        job_status[event.job_id] = {'status': 'success', 'last_run': event.scheduled_run_time}

def retry_on_failure(max_attempts=3, delay=10):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logger.error(f"作业执行失败 (尝试 {attempts}/{max_attempts}): {str(e)}")
                    if attempts < max_attempts:
                        time.sleep(delay)
            logger.critical(f"作业在 {max_attempts} 次尝试后仍然失败")
        return wrapper
    return decorator

def add_jobs(scheduler):
    """添加所有需要调度的作业"""
    # hello
    scheduler.add_job(hello_job, 'interval', seconds=5)

@retry_on_failure()  
def hello_job():
    logger.info("hello_job...")

if __name__ == '__main__':
    try:
        get_training_data()

        # 初始化调度器
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {'default': ProcessPoolExecutor(10)}
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'misfire_grace_time': 120
        }
        scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )

        # 添加作业和监听器
        add_jobs(scheduler)
        scheduler.add_listener(log_job_execution, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

        logger.info("调度器正在启动...")
        scheduler.start()
        logger.info("调度器已启动并正在运行...")

        # 主循环
        while True:
            time.sleep(600)
            # 定期检查作业状态
            for job_id, status in job_status.items(): 
                logger.info(f"作业 {job_id} 状态: {status['status']}, 上次运行: {status['last_run']}")

    except (KeyboardInterrupt, SystemExit):
        logger.info("捕获系统退出信号，准备关闭调度器...")
        scheduler.shutdown()
        logger.info("调度器已成功关闭")
        # 停止子进程
        stop_event.set()
        if stop_loss_process and stop_loss_process.is_alive():
            stop_loss_process.join(timeout=5)
            if stop_loss_process.is_alive():
                stop_loss_process.terminate()

    #logger.info("start server, docs: http://127.0.0.1:" + str(config.listen_port) + "/docs")
    #uvicorn.run(app="app.asgi:app", host=config.listen_host, port=config.listen_port, reload=config.reload_debug, log_level="warning")
