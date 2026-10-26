from celery import Celery

from TestRunner.core.TestRunner import TestRunner

# Redis 配置（存储任务状态）
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
# Celery 配置
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@celery.task(bind=True)
def run_tests(self, test_suite_config):
    """异步执行测试任务"""
    try:
        # 更新任务状态为运行中
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': '开始执行测试'})

        # 实例化测试运行器
        runner = TestRunner(test_suite_config)
        runner.run(async_mode=True)

        # 测试完成后返回结果
        return {
            'status': 'COMPLETED',
            'progress': 100,
            'results': runner.results,
            'stats': runner.stats
        }
    except Exception as e:
        return {
            'status': 'FAILED',
            'progress': 100,
            'error': str(e)
        }
