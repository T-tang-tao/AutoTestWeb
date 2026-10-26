import yaml
from typing import Any, Optional, Dict
from pathlib import Path

from utils import Common
from utils.LoggerManager import LoggerManager
logger = LoggerManager().get_logger()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "main.yml"


class ConfigLoader:
    """
    配置加载器（单例模式实现）
    支持从YAML文件加载配置，并提供手动重新加载功能
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, path: str = ''):
        if self._initialized:
            return
        if path is None:
            path = DEFAULT_CONFIG_PATH
        if not path:
            path = DEFAULT_CONFIG_PATH
        self.config = {}
        self.config_path = Path(path).expanduser().resolve()

        self._initialized = True
        self.load()

    def get_config(self):
        self.load()
        return self.config


    def load(self):
        """
        加载配置文件
        """
        if not self.config_path:
            logger.error(" 未初始化主配置文件路径，请先调用load()加载配置 ")
            raise RuntimeError("未初始化主配置文件路径")
        # 转换为绝对路径
        absconfig_path = Path(self.config_path).expanduser().resolve()
        self.config_path = absconfig_path

        try:
            """
            加载配置文件
            :param config_path: 配置文件路径
            """
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            for key in ("TestBedPath", "TestSetPath", "base_dir"):
                if self.config.get(key):
                    self.config[key] = self._resolve_path(self.config[key])

            with open(self.config['TestBedPath'], 'r', encoding='utf-8') as f:
                self.config['TestBed'] = yaml.safe_load(f)

            with open(self.config['TestSetPath'], 'r', encoding='utf-8') as f:
                self.config['TestSet'] = yaml.safe_load(f)

            return self.config

        except Exception as e:
            logger.error(f"加载配置失败: {str(e)}")
            raise

    def _resolve_path(self, value: str) -> str:
        """Resolve project configuration paths relative to main.yml."""
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = self.config_path.parent / path
        resolved = path.resolve()
        if resolved.exists():
            return str(resolved)

        # Keep older local configs usable after the project directory moves.
        candidates = (
            self.config_path.parent / path.name,
            PROJECT_ROOT / path.name,
        )
        for candidate in candidates:
            if candidate.exists():
                return str(candidate.resolve())
        return str(resolved)

    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置值（支持点分语法）"""
        if not self.config:
            logger.warning("配置未加载，返回默认值")
            return default

        keys = key_path.split('.')
        current = self.config

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                logger.warning(f"配置中未找到路径: {key_path}，返回默认值")
                return default
        return current

    def save_test_bed(self, test_bed_data: Dict):
        """保存TestBed配置到文件"""
        if not self.config_path:
            raise RuntimeError("请先调用load()加载配置")

        test_bed_path = self.get("TestBedPath")
        if not test_bed_path:
            raise ValueError("配置中缺少'TestBedPath'")
        path = Path(self._resolve_path(test_bed_path))

        try:
            # 确保目录存在
            directory = path.parent
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)

            # 写入配置文件
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(test_bed_data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

            # 更新内存中的配置
            self.config['TestBed'] = test_bed_data
            logger.info(f"成功保存TestBed配置到: {path}")
            self.load()
            # 刷新登录信息
            # Common.HuiXin_login(test_bed_data,refresh=True)
            return {"message": "TestBed配置保存成功", "path": str(path)}
        except Exception as e:
            logger.error(f"保存TestBed配置失败: {str(e)}")
            raise




if __name__ == "__main__":
    # 示例用法
    config_path = DEFAULT_CONFIG_PATH
    configLoader = ConfigLoader(path=config_path)
    config = configLoader.config

    test_bed = config['TestBed']
    print(test_bed)
