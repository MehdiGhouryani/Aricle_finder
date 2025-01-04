from apscheduler.schedulers.background import BackgroundScheduler

def start_scheduler(task_function):
    scheduler = BackgroundScheduler()
    scheduler.add_job(task_function, 'interval', days=1)
    scheduler.start()
