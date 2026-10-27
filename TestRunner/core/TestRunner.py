import ast
import importlib.util
import sys
import traceback
from pathlib import Path
from typing import List, Dict, Callable, Optional, Any
import threading
import uuid

from TestRunner.core.Base import StepStatus, TestStatus
from utils.Common import time_now, time_diff, HuiXin_login
from utils.ConfigLoader import ConfigLoader
from utils.LoggerManager import LoggerManager


class TestRunner:
    """
    测试运行器，负责加载和执行测试用例。
    支持同步和异步模式，提供测试进度跟踪功能。
    """

    def __init__(self, config, params=None, progress_callback: Callable = None):
        """初始化测试运行器
        params 为测试套传递自定义参数， 传入到测试用例中
        """
        self.logger = LoggerManager().get_logger()
        self.logger.info("===== 初始化测试运行器 =====")
        # 测试用例实例列表
        self.test_instances: List[Any] = []
        self._loaded_module_names: List[str] = []

        self.total_set_cases_num = 0  # 测试套总用例数（配置中定义的）
        self.loaded_cases_num = 0  # 实际加载成功的用例数
        self.test_set_error = None  # 测试套错误消息
        self.load_errors: List[str] = []  # 未能加载的用例及错误原因
        self.test_set_status = TestStatus.PENDING.value  # 测试套整体状态（核心优化：初始化为待执行）
        self.test_set_all_steps_num = 0  # 所有测试步骤数量（计算进度用）

        self.progress_callback = progress_callback
        self.params = params
        self.results: List[Dict] = []
        self.stats = {'total': 0, 'passed': 0, 'failed': 0, 'error': 0, 'skipped': 0}

        self.completed_tests = 0  # 已完成的用例数（用于进度计算）
        self.is_running = False
        self.stop_event = threading.Event()
        self.task_id = str(uuid.uuid4())
        self.overall_start_time = None  # 整体测试开始时间
        self.overall_end_time = None  # 整体测试结束时间

        # 校验参数
        self._validate_config(config)
        self.logger.info(f"测试任务ID: {self.task_id}")

    def _validate_config(self, config):
        """验证测试配置的有效性"""
        self.logger.info(f"[配置校验] 开始校验测试配置文件及参数 \n {config}")

        # 核心配置项校验
        required_fields = ["TestBed", "TestSet", "base_dir"]
        for field in required_fields:
            if field not in config:
                error_msg = f"[配置校验] 配置文件缺少必填字段: {field}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

        # 解析基础配置
        self.test_bed = config['TestBed']
        self.test_set = config['TestSet']
        self.base_dir = Path(config['base_dir'])
        self.logger.info(f"[配置校验] 测试根目录: {self.base_dir.absolute()}")
        self.logger.info(f"[配置校验] 测试环境(TestBed): {self.test_bed.get('env', '未命名环境')}")

        # 初始化登录信息cookie
        self.user_cookie = HuiXin_login(self.test_bed)

        # 测试用例路径校验
        if 'test_cases' not in self.test_set:
            error_msg = "[配置校验] TestSet中缺少test_cases字段"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.total_set_cases_num = len(self.test_set['test_cases'])
        self.logger.info(f"[配置校验] 测试套包含用例数: {self.total_set_cases_num}")

        if self.total_set_cases_num == 0:
            self.logger.warning("[配置校验] 测试套中未包含任何测试用例，执行将跳过")
            return

        for idx, test_case in enumerate(self.test_set['test_cases'], 1):
            if 'path' not in test_case:
                error_msg = f"[配置校验] 第{idx}个用例缺少path字段(脚本路径)"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            case_path = self.base_dir / test_case['path']
            if not case_path.exists():
                error_msg = f"[配置校验] 第{idx}个用例路径不存在: {case_path.absolute()}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

    def run(self, async_mode: bool = False) -> Optional[str]:
        """执行测试套件（同步/异步模式）"""
        self.logger.info(f"[测试启动] 开始执行测试套")
        # 优化：测试套开始执行时，更新状态为"运行中"
        self.test_set_status = TestStatus.RUNNING.value
        if async_mode:
            thread = threading.Thread(target=self._execute_tests, name=f"TestRunner-{self.task_id[:8]}")
            thread.daemon = True
            thread.start()
            self.logger.info(f"[测试启动] 任务已启动，任务ID: {self.task_id}")
            return self.task_id
        else:
            self._execute_tests()
            return None

    def stop(self):
        """停止正在执行的测试"""
        self.stop_event.set()
        self.is_running = False
        # 优化：手动终止时，更新测试套状态为"已取消"
        # self.test_set_status = TestStatus.CANCELLED.value
        self.logger.warning(f"[测试终止] 测试任务 {self.task_id} 已手动终止")

    # -------------------------
    # 测试执行流程控制
    # -------------------------
    def _execute_tests(self):
        """执行所有测试用例的主流程"""
        try:
            cases_initialized = self._init_test_cases()
        except Exception as exc:
            # Initialization failures are framework errors, not assertion failures.
            self.test_set_status = TestStatus.ERROR.value
            self.test_set_error = self.test_set_error or str(exc)
            self.overall_end_time = self.overall_end_time or time_now()
            self._refresh_stats()
            self._cleanup_loaded_modules()
            self.is_running = False
            raise

        if cases_initialized:
            try:
                if self.loaded_cases_num == 0:
                    self.logger.warning("[测试执行] 无可用测试用例，终止执行")
                    self.test_set_status = TestStatus.PASS.value  # 无可用用例视为"通过"
                    return

                # 初始化测试套状态为"运行中"
                self.test_set_status = TestStatus.RUNNING.value
                self.logger.info("\n" + "=" * 60)
                self.logger.info(f"[用例执行] 开始执行{self.loaded_cases_num}个测试用例")
                self.logger.info("=" * 60 + "\n")

                # 循环执行用例  初始化测试执行器执行时间
                self.overall_start_time = time_now()
                for case_idx, test_instance in enumerate(self.test_instances, 1):
                    case_name = test_instance.__class__.__name__
                    # 用例开始执行时，更新状态为"运行中"
                    test_instance.test_status = TestStatus.RUNNING.value
                    self.logger.info(
                        f"[用例执行] 开始执行用例 {case_idx}/{self.loaded_cases_num}: {case_name}，状态: {test_instance.test_status}")

                    test_instance.execute_start_time = time_now()
                    try:
                        # 执行前置步骤
                        self._run_test_case_step(test_instance, test_instance.setUp, "前置步骤", case_name)
                        # 执行核心用例步骤
                        self._execute_test_case(test_instance)
                        # 执行后置步骤
                        self._run_test_case_step(test_instance, test_instance.tearDown, "后置步骤", case_name)
                        # 用例成功执行完成
                        test_instance.test_status = TestStatus.PASS.value
                        self.logger.info(
                            f"[用例执行] 用例 {case_idx}/{self.loaded_cases_num}: {case_name} 执行成功，状态更新为: {test_instance.test_status}")
                    except AssertionError as e:
                        # 用例断言失败
                        test_instance.test_status = TestStatus.FAIL.value
                        self.logger.error(
                            f"[用例执行] 用例 {case_idx}/{self.loaded_cases_num}: {case_name} 断言失败: {str(e)}，状态更新为: {test_instance.test_status}")
                    except Exception as e:
                        # 用例执行异常
                        test_instance.test_status = TestStatus.ERROR.value
                        self.logger.error(
                            f"[用例执行] 用例 {case_idx}/{self.loaded_cases_num}: {case_name} 执行异常: {str(e)}，状态更新为: {test_instance.test_status}")
                        self.logger.debug(f"[用例执行] 异常堆栈:\n{traceback.format_exc()}")
                    finally:

                        # 记录用例结束时间和耗时
                        test_instance.execute_end_time = time_now()
                        test_instance.execute_duration = time_diff(test_instance.execute_start_time,
                                                                   test_instance.execute_end_time)
                        self.logger.info(
                            f"[用例执行] 用例 {case_idx}/{self.loaded_cases_num}: {case_name} 执行结束，耗时: {test_instance.execute_duration:.2f}s，最终状态: {test_instance.test_status}\n")

                        self.completed_tests += 1

                # 所有用例执行完毕或被终止后更新测试套状态
                # 检查所有用例是否全部通过
                all_passed = (
                    not self.load_errors
                    and all(
                        test.test_status == TestStatus.PASS.value
                        for test in self.test_instances
                    )
                )
                self.test_set_status = TestStatus.PASS.value if all_passed else TestStatus.FAIL.value
                self._refresh_stats()
            finally:
                self.overall_end_time = time_now()
                total_duration = time_diff(self.overall_start_time, self.overall_end_time)
                self.logger.info("=" * 60)
                self.logger.info(f"[测试结束] 所有用例执行完成，测试套最终状态: {self.test_set_status}")
                self.logger.info(f"[测试结束] 结束时间: {self.overall_end_time}")
                self.logger.info(f"[测试结束] 总耗时: {total_duration:.2f}s")
                self.logger.info("=" * 60)

                self._log_test_summary()
                self._cleanup_loaded_modules()
                self.is_running = False
        else:
            self.logger.error("[测试结束] 测试套初始化失败，终止执行")
            self.test_set_status = TestStatus.FAIL.value
            if not self.test_set_error:
                if self.total_set_cases_num == 0:
                    self.test_set_error = "测试套中没有配置用例"
                else:
                    self.test_set_error = "测试套中没有成功加载任何用例"
            self.overall_end_time = self.overall_end_time or time_now()
            self._refresh_stats()
            self._cleanup_loaded_modules()
            self.is_running = False
            return

    def _init_test_cases(self):
        """初始化测试用例   统计测试用例总数 步骤   获取测试用例实例"""
        self.is_running = True
        self.completed_tests = 0
        self.overall_start_time = time_now()  # 记录整体开始时间
        self.logger.info("=" * 60)
        self.logger.info(f"[用例加载] 开始执行测试套，总用例数: {self.total_set_cases_num}")
        self.logger.info(f"[用例加载] 整体开始时间: {self.overall_start_time}")
        self.logger.info("=" * 60)

        self.logger.info("[用例加载] 开始遍历加载测试用例...")
        for idx, test_case in enumerate(self.test_set['test_cases'], 1):
            if self.stop_event.is_set():
                self.logger.warning("[用例加载] 收到终止信号，停止加载用例")
                break
            case_path = test_case['path']
            self.logger.info(f"[用例加载] 正在加载第{idx}/{self.total_set_cases_num}个用例: {case_path}")
            try:
                # 加载用例实例
                case_instance = self._load_case_instance(case_path)
                if not case_instance:
                    if not self.load_errors:
                        error_msg = f"[用例加载] 第{idx}个用例加载失败: {case_path}"
                        self.load_errors.append(error_msg)
                        self.test_set_error = error_msg
                    # A failed-to-load case is still an accounted-for case.
                    self.completed_tests += 1
                    self.logger.error(f"[用例加载] 第{idx}个用例加载失败，跳过该用例")
                    continue
                self.logger.info(f"[测试步骤加载] 开始加载用例测试步骤")
                self.logger.debug(
                    '[备注] 只记录测试步骤，如果在测试步骤加载完成之前执行了代码，说明defineSteps 中的def_step 没有实现懒加载数据')
                case_instance.defineSteps()  # 定义步骤（不执行）
                step_count = len(case_instance.step_plans)
                self.logger.info(f"[测试步骤加载] 成功 用例 {case_path} 包含 {step_count} 个测试步骤")
                self.test_set_all_steps_num += step_count
                self.test_instances.append(case_instance)
                self.loaded_cases_num += 1  # 记录加载成功的用例数
                self.logger.info(
                    f"[用例加载] 第{idx}个用例加载成功，包含步骤数: {step_count}，初始状态: {case_instance.test_status}")
            except Exception as e:
                self.logger.error(f"[用例加载失败] 第{idx}个用例加载异常: {str(e)}")
                self.logger.debug(f"[用例加载] 异常堆栈:\n{traceback.format_exc()}")
                self.test_set_error = f"[用例加载] 第{idx}个用例加载异常: {str(e)}"
                self.overall_end_time = time_now()
                self.test_set_status = TestStatus.FAIL.value
                raise
        if self.loaded_cases_num == 0:
            return False
        else:
            self.logger.info(
                f"[用例加载] 用例加载完成，成功加载{self.loaded_cases_num}/{self.total_set_cases_num}个用例")
            return True

    def _execute_test_case(self, test_instance):
        """执行单个测试用例的完整生命周期"""
        test_name = test_instance.__class__.__name__
        self.logger.info(f"[步骤执行] 开始执行用例 {test_name} 的测试步骤")
        self._run_test_steps(test_instance)

    def _run_test_steps(self, test_instance):
        """执行测试用例中定义的所有步骤"""
        test_name = test_instance.__class__.__name__
        total_steps = test_instance.step_plans
        step_count = len(total_steps)

        if step_count == 0:
            self.logger.warning(f"[步骤执行] 用例 {test_name} 未定义任何测试步骤")
            return

        self.logger.info(f"[步骤执行] 用例 {test_name} 包含{step_count}个步骤，开始执行...")

        for step_idx, step in enumerate(total_steps, 1):
            # 步骤初始化
            step["status"] = StepStatus.RUNNING.value
            step['start_time'] = time_now()
            step_name = step["name"]
            args = step["args"] or ()
            kwargs = step["kwargs"] or {}

            self.logger.info(f"\n[步骤执行] 用例 {test_name} - 步骤 {step_idx}/{step_count}: {step_name} (开始)")
            self.logger.debug(f"[步骤参数] args: {args}, kwargs: {kwargs}")

            try:
                # 解析延迟参数并执行步骤
                resolved_kwargs = self._resolve_lazy_parameters(kwargs)
                step["method"](*args, **resolved_kwargs)

                # 步骤成功
                step["status"] = StepStatus.PASS.value
                step['end_time'] = time_now()
                step["duration"] = time_diff(step["start_time"], step["end_time"])
                self.logger.info(
                    f"[步骤执行] 用例 {test_name} - 步骤 {step_idx}/{step_count}: {step_name} (成功)，耗时: {step['duration']:.2f}s")

            except AssertionError as e:
                # 断言失败
                step["status"] = StepStatus.FAIL.value
                step["error"] = f"断言失败: {str(e)}"
                step['end_time'] = time_now()
                step["duration"] = time_diff(step["start_time"], step["end_time"])
                self.logger.error(
                    f"[步骤执行] 用例 {test_name} - 步骤 {step_idx}/{step_count}: {step_name} (失败)，耗时: {step['duration']:.2f}s")
                self.logger.error(f"[失败原因] {step['error']}")
                test_instance.is_failed = True
                # 跳过后续步骤
                self._skip_remaining_steps(test_instance, step_idx, step_count, test_name)
                raise
            except Exception as e:
                # 执行异常
                step["status"] = StepStatus.ERROR.value
                step["error"] = f"{type(e).__name__}: {str(e)}"
                step['end_time'] = time_now()
                step["duration"] = time_diff(step["start_time"], step["end_time"])
                self.logger.error(
                    f"[步骤执行] 用例 {test_name} - 步骤 {step_idx}/{step_count}: {step_name} (异常)，耗时: {step['duration']:.2f}s")
                self.logger.error(f"[异常原因] {step['error']}")
                self.logger.debug(f"[异常堆栈] {traceback.format_exc()}")
                test_instance.is_failed = True
                self._skip_remaining_steps(test_instance, step_idx, step_count, test_name)
                raise

    # -------------------------
    # 步骤执行和结果记录（其余方法保持不变）
    # -------------------------
    def _run_test_case_step(self, test_instance, method, step_name: str, case_name: str):
        """执行测试用例级别的步骤（前置/后置）"""
        self.logger.info(f"[用例{case_name}] {step_name} 开始执行")
        try:
            method()
            self.logger.info(f"[用例{case_name}] {step_name} 执行成功")
        except Exception as e:
            self.logger.error(f"[用例{case_name}] {step_name} 执行失败: {str(e)}")
            test_instance.error = f"[{step_name}] {case_name}  执行失败: {str(e)}  {traceback.format_exc()}"
            raise

    def _skip_remaining_steps(self, test_instance, current_step_idx: int, total_steps: int, case_name: str):
        """将剩余未执行的步骤状态设置为"跳过"并通知"""
        skip_start = current_step_idx + 1
        if skip_start > total_steps:
            return

        self.logger.warning(f"[用例{case_name}] 步骤 {current_step_idx} 失败，将跳过后续步骤 {skip_start}-{total_steps}")
        for idx in range(skip_start, total_steps + 1):
            step = test_instance.step_plans[idx - 1]  # 列表索引从0开始
            step["status"] = StepStatus.SKIP.value
            step["skip_reason"] = f"因步骤 {current_step_idx} 失败"
            self.logger.info(f"[用例{case_name}] 步骤 {idx}/{total_steps}: {step['name']} (已跳过)")

    def _resolve_lazy_parameters(self, kwargs):
        """解析延迟执行的参数"""
        resolved_kwargs = {}
        try:
            for key, value in kwargs.items():
                if isinstance(value, dict) and value.get("is_callable"):
                    self.logger.debug(f"[参数解析] 延迟执行参数 {key}: {value['callable'].__name__}()")
                    resolved_kwargs[key] = value["callable"]()
                else:
                    resolved_kwargs[key] = value
            return resolved_kwargs
        except Exception as e:
            raise e

    def _load_case_instance(self, case_path: str):
        """Load one case with a task-unique module key to avoid cross-run collisions."""
        full_path = self.base_dir / Path(case_path)
        module_name = full_path.stem
        module_key = f"_autotestweb_case_{self.task_id.replace('-', '')}_{module_name}"

        try:
            spec = importlib.util.spec_from_file_location(module_key, full_path)
            if not spec or not spec.loader:
                raise ImportError(f"无法创建模块规格: {full_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_key] = module
            spec.loader.exec_module(module)

            # Keep the file/class naming convention independent from the import key.
            test_class = getattr(module, module_name, None)
            if not test_class:
                self.test_set_error = f"模块中未找到测试类 {module_name} (约定类名与模块名一致)"
                self.test_set_status = StepStatus.ERROR.value
                raise AttributeError(f"模块中未找到测试类 {module_name} (约定类名与模块名一致)")
            # 新增：解析case_name并绑定到实例
            case_name = self._get_case_name_from_file(full_path)
            instance = test_class(params=self.params, user_cookie=self.user_cookie) if self.params else test_class(
                user_cookie=self.user_cookie)
            instance.case_name = case_name  # 将case_name绑定到实例
            self._loaded_module_names.append(module_key)
            self.logger.debug(f"[模块加载] 成功加载用例: {case_name} (类名: {module_name})")
            return instance

        except Exception as e:
            sys.modules.pop(module_key, None)
            if module_key in self._loaded_module_names:
                self._loaded_module_names.remove(module_key)
            error_msg = (
                f"[模块加载] 加载模块 {module_name} 失败: "
                f"{type(e).__name__}: {e}"
            )
            self.load_errors.append(error_msg)
            self.test_set_error = "; ".join(self.load_errors)
            self.logger.error(error_msg)
            self.logger.debug(f"[异常堆栈] {traceback.format_exc()}")
            return None

    def _cleanup_loaded_modules(self) -> None:
        """Remove temporary module registrations created by this runner."""
        for module_name in self._loaded_module_names:
            sys.modules.pop(module_name, None)
        self._loaded_module_names.clear()

    def cleanup_resources(self) -> None:
        """Release case instances after an external task has captured its result."""
        self._cleanup_loaded_modules()
        self.test_instances.clear()
        self.results.clear()

    def _get_case_name_from_file(self, file_path: Path) -> str:
        """从测试用例文件中静态解析case_name（不执行代码）"""
        if not file_path.exists() or file_path.suffix != ".py":
            return file_path.stem  # 默认返回文件名（不含后缀）

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == 'case_name':
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                return node.value.value.strip() or file_path.stem
            return file_path.stem  # 未找到case_name时返回文件名
        except Exception as e:
            self.logger.warning(f"解析{file_path}的case_name失败: {e}，将使用文件名作为用例名")
            return file_path.stem

    def _calculate_progress(self) -> float:
        """计算测试进度百分比"""
        if self.total_set_cases_num == 0:
            return 100.0
        return min(100.0, (self.completed_tests / self.total_set_cases_num) * 100)

    def _refresh_stats(self) -> None:
        """Update aggregate case counts from the final per-case results."""
        error_count = (
            sum(
                1 for case in self.test_instances
                if case.test_status == TestStatus.ERROR.value
            )
            + len(self.load_errors)
        )
        if self.total_set_cases_num and self.test_set_error and error_count == 0:
            error_count = 1

        self.stats = {
            "total": self.total_set_cases_num,
            "passed": sum(
                1 for case in self.test_instances
                if case.test_status == TestStatus.PASS.value
            ),
            "failed": sum(
                1 for case in self.test_instances
                if case.test_status == TestStatus.FAIL.value
            ),
            "error": error_count,
            "skipped": sum(
                1 for case in self.test_instances
                if case.test_status == TestStatus.SKIP.value
            ),
        }

    def _log_test_summary(self):
        """打印测试总结报告（结构化输出）"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("               测试执行总结报告")
        self.logger.info(f"               测试套状态: {self.test_set_status}")  # 打印整体状态
        self.logger.info("=" * 60)

        # 统计用例状态
        passed = sum(1 for inst in self.test_instances if inst.test_status == TestStatus.PASS.value)
        failed = sum(1 for inst in self.test_instances if inst.test_status == TestStatus.FAIL.value)
        error = sum(1 for inst in self.test_instances if inst.test_status == TestStatus.ERROR.value)
        running = sum(1 for inst in self.test_instances if inst.test_status == TestStatus.RUNNING.value)
        pending = sum(1 for inst in self.test_instances if inst.test_status == TestStatus.PENDING.value)
        total = len(self.test_instances)

        # 打印汇总统计
        self.logger.info(f"总用例数: {total}")
        self.logger.info(f"通过用例: \033[32m{passed}\033[0m ({passed / total * 100:.1f}%)")
        self.logger.info(f"失败用例: \033[31m{failed}\033[0m ({failed / total * 100:.1f}%)")
        self.logger.info(f"异常用例: \033[33m{error}\033[0m ({error / total * 100:.1f}%)")
        self.logger.info(f"运行中用例: \033[34m{running}\033[0m")
        self.logger.info(f"待执行用例: \033[35m{pending}\033[0m")
        self.logger.info("-" * 60)

        # 打印每个用例详情
        for idx, inst in enumerate(self.test_instances, 1):
            case_name = inst.__class__.__name__
            status = inst.test_status
            duration = getattr(inst, "execute_duration", 0)
            # 根据状态设置颜色
            if status == TestStatus.PASS.value:
                status_color = "\033[32m"
            elif status == TestStatus.FAIL.value:
                status_color = "\033[31m"
            elif status == TestStatus.ERROR.value:
                status_color = "\033[33m"
            elif status == TestStatus.RUNNING.value:
                status_color = "\033[34m"
            else:
                status_color = "\033[35m"
            self.logger.info(f"用例 {idx}: {case_name}")
            self.logger.info(f"  状态: {status_color}{status}\033[0m")
            self.logger.info(f"  耗时: {duration:.2f}s")
            self.logger.info(f"  步骤数: {len(inst.step_plans)}")
            self.logger.info("  ---")

        self.logger.info("=" * 60 + "\n")

    def get_test_instances_details(self) -> Dict:
        """获取所有测试实例的详细信息（优化：使用统一状态）"""
        # 1. 收集所有测试实例及步骤详情
        instances_details = []

        total_steps = 0  # 总步骤数（所有用例）
        passed_steps = 0  # 通过的步骤数
        skipped_steps = 0  # 跳过的步骤数
        failed_steps = 0  # 失败的步骤数
        error_steps = 0


        for instance in self.test_instances:
            total_steps += len(instance.step_plans)
            for step in instance.step_plans:
                if step["status"] == StepStatus.PASS.value:
                    passed_steps += 1
                elif step["status"] == StepStatus.FAIL.value:
                    failed_steps += 1
                elif step["status"] == StepStatus.ERROR.value:
                    error_steps += 1
                elif step["status"] == StepStatus.SKIP.value:
                    skipped_steps += 1

            # 提取测试实例基本信息
            instance_info = {
                "test_class_name": instance.__class__.__name__,
                "test_instance_name": instance.case_name or instance.__class__.__name__,
                "test_status": instance.test_status,  # 单个用例状态
                "steps": instance.step_plans,
                "start_time": getattr(instance, "execute_start_time", None),
                "end_time": getattr(instance, "execute_end_time", None),
                "duration": getattr(instance, "execute_duration", None),
                "error": getattr(instance, "error", None),
                # 单个用例的步骤统计
                "case_step_stats": {
                    "total": len(instance.step_plans),
                    "passed": sum(1 for s in instance.step_plans if s["status"] == StepStatus.PASS.value),
                    "failed": sum(1 for s in instance.step_plans if s["status"] == StepStatus.FAIL.value),
                    "error": sum(1 for s in instance.step_plans if s["status"] == StepStatus.ERROR.value),
                    "skipped": sum(1 for s in instance.step_plans if s["status"] == StepStatus.SKIP.value),
                }
            }
            instances_details.append(instance_info)

        # 优化：直接使用统一计算的测试套状态，而非重复逻辑
        return {
            "status": self.test_set_status,  # 测试套整体状态（核心优化）
            "start_time": self.overall_start_time,
            "end_time": self.overall_end_time,
            "duration": self.overall_end_time and time_diff(self.overall_start_time, self.overall_end_time) or 0,
            "error": self.test_set_error,
            "progress": {
                "steps_stats": {
                    "total_steps": total_steps,
                    "passed_steps": passed_steps,
                    "failed_steps": failed_steps,
                    "error_steps": error_steps,
                    "skipped_steps": skipped_steps,
                },
                "case_stats": {
                    "total_cases": len(self.test_instances),  # 加载成功的用例总数
                    "passed": sum(1 for inst in self.test_instances if inst.test_status == TestStatus.PASS.value),
                    "failed": sum(1 for inst in self.test_instances if inst.test_status == TestStatus.FAIL.value),
                    "error": sum(1 for inst in self.test_instances if inst.test_status == TestStatus.ERROR.value),
                    "running": sum(1 for inst in self.test_instances if inst.test_status == TestStatus.RUNNING.value),
                    "pending": sum(1 for inst in self.test_instances if inst.test_status == TestStatus.PENDING.value),
                }
            },
            "test_cases": instances_details,  # 所有测试实例详情
        }
