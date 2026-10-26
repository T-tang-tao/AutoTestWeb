import logging
from enum import Enum
from typing import Callable, Optional, Tuple, Any, List, Dict

from utils.LoggerManager import LoggerManager

logger = LoggerManager().get_logger()


class TestStatus(Enum):
    """测试用例级状态枚举"""
    PASS = "通过"
    FAIL = "失败"
    ERROR = "错误"
    SKIP = "跳过"
    RUNNING = "进行中"
    PENDING = "待执行"


class StepStatus(Enum):
    """测试步骤级状态枚举"""
    PASS = "通过"
    FAIL = "失败"
    ERROR = "错误"
    SKIP = "跳过"
    RUNNING = "进行中"
    PENDING = "待执行"
    AUDIT = "审核中"
    FINISHED = "已完成"


class Base:
    """测试基类：负责测试步骤的定义和结果存储"""

    def __init__(self,**kwargs):

        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        self.test_status: Optional[str] = None

        self.step_plans: List[Dict[str, Any]] = []  # 步骤计划  执行更新状态
        self.is_failed: bool = False

        self.execute_start_time = None
        self.execute_end_time = None
        self.duration: float = 0.0


    def setUp(self) -> None:
        """测试前置条件（可被子类重写）"""
        pass

    def defineSteps(self) -> None:
        """定义测试步骤（子类必须实现）"""
        raise NotImplementedError("子类必须实现defineSteps方法")

    def tearDown(self) -> None:
        """测试后置操作（可被子类重写）"""
        self.logger.info("执行后置步骤...")

    def def_step(self, step_name: str, method: Callable, args: Optional[Tuple] = None,
                 kwargs: Optional[Dict] = None) -> None:
        """定义测试步骤（仅记录，不执行）"""
        try:
            self.logger.debug(f"记录测试步骤： {step_name}  初始化测试步骤状态 {StepStatus.PENDING.value}")
            processed_kwargs = {
                k: ({"is_callable": True, "callable": v} if callable(v) else v)
                for k, v in (kwargs or {}).items()
            }

            self.step_plans.append({
                "name": step_name,
                "status": StepStatus.PENDING.value,
                "method": method,
                "args": args or (),
                "kwargs": processed_kwargs,
            })
        except Exception as e:
            raise Exception(f"记录测试步骤失败：{step_name} {e}")
