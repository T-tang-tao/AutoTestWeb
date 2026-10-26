from pathlib import Path
from typing import List, Dict
import json
import ast


def _parse_variable_from_file(file_path: Path, var_name: str, fallback: str) -> str:
    """
    通用函数：从文件中静态解析指定变量的值

    :param file_path: 目标文件路径（.py）
    :param var_name: 要提取的变量名（如module_name、case_name）
    :param fallback: 提取失败时的默认值
    :return: 变量值或默认值
    """
    if not file_path.exists() or not file_path.is_file() or file_path.suffix != ".py":
        return fallback

    try:
        # 静态解析文件内容，不执行代码
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        # 遍历AST节点，寻找目标变量的赋值
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == var_name:
                        # 仅支持简单字符串赋值（如 var_name = "xxx"）
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            return node.value.value.strip() or fallback
        return fallback  # 未找到变量时返回默认值
    except Exception as e:
        print(f"解析{file_path}的{var_name}失败: {e}")
        return fallback  # 解析出错时返回默认值


def get_module_name(dir_path: Path) -> str:
    """从目录的__init__.py中获取module_name（无则用目录名）"""
    init_file = dir_path / "__init__.py"
    return _parse_variable_from_file(
        file_path=init_file,
        var_name="module_name",
        fallback=dir_path.name  # 默认用目录名
    )


def get_case_name(py_file: Path) -> str:
    """从.py文件中获取case_name（无则用文件名，不含后缀）"""
    return _parse_variable_from_file(
        file_path=py_file,
        var_name="case_name",
        fallback=py_file.stem  # 默认用文件名（不含.py）
    )


def traverse_test_cases(root_dir: str) -> List[Dict]:
    """遍历Business目录，统一解析所有名称"""
    business_dir = Path(root_dir)
    if not business_dir.exists() or not business_dir.is_dir():
        return []

    result = []
    # 遍历Business下的一级目录（模块根目录）
    for module_dir in sorted(business_dir.iterdir()):
        if not module_dir.is_dir():
            continue

        # 模块根目录名称（来自__init__.py的module_name）
        module_name = get_module_name(module_dir)

        # 查找TestCases目录
        test_cases_dir = module_dir / "TestCases"
        if not test_cases_dir.is_dir():
            continue

        # 递归处理TestCases下的所有内容
        def traverse_dir(current_dir: Path) -> List[Dict]:
            items = []
            for item in sorted(current_dir.iterdir()):
                # 过滤不需要的文件/目录
                if item.name == "__pycache__" and item.is_dir():
                    continue
                if item.name == "__init__.py" and item.is_file():
                    continue

                # 统一路径分隔符
                full_path = str(item).replace("\\", "/")
                item_info = {"path": full_path}

                if item.is_dir():
                    # 子目录名称（来自自身__init__.py的module_name）
                    dir_name = get_module_name(item)
                    children = traverse_dir(item)
                    if children:
                        item_info.update({
                            "label": dir_name,
                            "type": "folder",
                            "children": children,
                            "isLeaf": False
                        })
                        items.append(item_info)
                else:
                    # 测试用例文件（来自自身的case_name）
                    if item.suffix == ".py":
                        case_name = get_case_name(item)
                        item_info.update({
                            "label": case_name,
                            "type": "file",
                            "ext": ".py",
                            "isLeaf": True
                        })
                        items.append(item_info)
            return items

        # 处理当前模块的测试用例
        test_cases = traverse_dir(test_cases_dir)
        if test_cases:
            result.append({
                "label": module_name,
                "type": "module",
                "path": str(test_cases_dir).replace("\\", "/"),
                "children": test_cases,
                "isLeaf": False
            })

    return result


# 示例用法
if __name__ == "__main__":
    business_dir = Path(__file__).resolve().parents[2] / "Business"
    test_data = traverse_test_cases(business_dir)
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
