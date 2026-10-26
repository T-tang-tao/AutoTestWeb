from enum import Enum

from utils.ConfigLoader import ConfigLoader


# 评估流程参数
# sc_prison_process
class Assessment(Enum):
    # 入监评估大包
    入监评估 = {'flowIds': [
        "xt7so3gxb___S1",  # 改造难易度评估【入监】
        "sd5nvp72g___S1",  # 职业能力评估【入监】
        "szbimy6nj___S1",  # 个体危险性评估流程【入监】
        "oimd21znw___S1",  #
        "vfg94ckfg___S1",  # 【罪犯填写】入监信息采集
        "xo43w4aso___S1"  # 【民警填写】罪犯体检信息采集
    ], 'packageCode': 'ifYNqmzJXf', 'folderName': '入监评估'}

    # 罪犯基本信息采集
    入监_罪犯基本信息采集 = {'flowIds': ["vfg94ckfg___S1", "xo43w4aso___S1"], 'packageCode': 'WGVAy54IP',
                             'folderName': '罪犯基本信息采集【入监】'}

    入监_罪犯基本信息采集_罪犯 = {'flowIds': ["vfg94ckfg___S1"], 'packageCode': 'WGVAy54IP',
                             'folderName': '【罪犯填写】入监信息采集'}

    入监_罪犯基本信息采集_民警 = {'flowIds': ["xo43w4aso___S1"],'packageCode': 'WGVAy54IP',
                             'folderName': '【民警填写】罪犯体检信息采集'}

    # 罪犯基本信息采集
    入监_职业技能评估 = {'flowIds': ["sd5nvp72g___S1"], 'packageCode': 'Tn7JpfW4U',
                         'folderName': '职业技能评估【入监】'}

    入监_改造难易度评估 = {'flowIds': ["xt7so3gxb___S1"], 'packageCode': 'MHlVClNWJg',
                           'folderName': '改造难易度评估【入监】'}

    # 入监个体危险性评估
    入监_个体危险性评估 = {'flowIds': ["szbimy6nj___S1"], 'packageCode': 'qouH93PRn',
                           'folderName': '个体危险性评估流程【入监】'}

    入监_身心健康评估 = {'flowIds': ["oimd21znw___S1"], 'packageCode': 'JgbkllVno',
                         'folderName': '身心健康评估流程【入监】'}

    # 中期评估
    # 中期个体危险性评估
    中期_个体危险性评估 = {'flowIds': ["d5hmjbha8___S1"], 'packageCode': 'VL7JVywaR',
                           'folderName': '个体危险性评估流程【中期】'}

    中期_访谈辅助评估 = {'flowIds': ["3zhystmae___S1"], 'packageCode': 'Dt8w94qbY',
                           'folderName': '访谈辅助评估流程【中期】'}


    中期_改造难易度评估 = {'flowIds': ["qstxohl66___S1"], 'packageCode': '9F5SPJjCp',
                           'folderName': '改造难易度评【中期】'}

    中期_职业技能评估 = {'flowIds': ["hj5wchp5q___S1"], 'packageCode': 'gbSOfD9vL',
                         'folderName': '职业技能评估【中期】'}

    中期_身心健康评估 = {'flowIds': ["93vpn49km___S1"], 'packageCode': '5eMWcSppey',
                         'folderName': '身心健康评估流程【中期】'}

    中期_认罪悔改表现评估 = {'flowIds': ["5aywatnh4___S1"], 'packageCode': 'ohYzku6f7',
                         'folderName': '认罪悔改表现评估【中期】'}

    # 出监评估  大包
    出监评估 = {'flowIds': [
        "m9JjOGYzF",  # 社会适应性评估【出监】
        "u3LRxqkLE",  # 再犯罪评估【出监】
        "aVW6k2Lw8",  # 职业技能评估【出监】

    ], 'packageCode': 'egZjoq86co', 'folderName': '出监评估'}

    出监评估_再犯罪评估 = {'flowIds': ["2fplawom6___S1"], 'packageCode': 'u3LRxqkLE',
                           'folderName': '再犯罪评估【出监】'}

    出监评估_社会适应性评估 = {'flowIds': ["m9JjOGYzF"], 'packageCode': 'm9JjOGYzF',
                               'folderName': '社会适应性评估【出监】'}

    出监评估_职业技能评估 = {'flowIds': ["m9JjOGYzF"], 'packageCode': 'aVW6k2Lw8',
                             'folderName': '职业技能评估【出监】'}


class Process(Enum):
    入监_罪犯_入监信息流程 = 'vfg94ckfg___S1'
    入监_民警_罪犯体检信息流程 = 'xo43w4aso___S1'
    入监_改造难易度流程 = 'xt7so3gxb___S1'
    入监_职业能力流程 = 'sd5nvp72g___S1'
    入监_个体危险性流程 = 'szbimy6nj___S1'
    入监_个体危险性评估审批流程 = "yv69eftqb___S1"
    入监_身心健康流程 = 'oimd21znw___S1'

    入监_基本信息采集审批 = 'znflzq8y5___S1'

    个体危险性评估_中期 = 'd5hmjbha8___S1'


    审核流程_个体危险性评估_中期 = 'sf76dvicv___S1'

    出监_再犯罪审核 = 'rft8coh3o___S1'


# 流程图  流程code
class ProcessNode(Enum):
    # 入监
    犯罪情况 = '4H6GTv4TK'
    身心健康评估量表='AC74eR1eVm'

    身心健康_辅助检查详细指标 = 'SRRMyeqWYS'
    入监体检表 = 'DD1XHpFp83'
    罪犯行为观察表 = 'aIFeCyY6MW'
    个体危险性量表 = 's3QMVXVFi9'
    个体危险评估报告_入监 = 'dEh9y4176'

    ja_身心健康_辅助检查 = '6IidQiK7ZH'
    ja_矫正案例 = 'W6KqF1lM4X'

    个体危险性中期评估审批表 = 'HzMn3BbM9P'

    # 出监
    社会适应性民警他评问卷 = 'ammgYBZvS'

    悔改表现权重确认表单 = 'lus6DfvkM'

    再犯罪报告 = '6LNxyfXHWO'

    访谈辅助问卷 = 'U07PZLeFzB'


class ProcessStepStatus(Enum):
    DOING = '进行中'
    PASS = '已通过'
    FINISHED = '已完成'


# 用户类型
class HUIXIN_USER(Enum):
    criminal = '罪犯'
    admin = '系统管理员'
    prison_police = '主管民警'
    doctor_police = '监狱医生'
    leader_police = '监区领导'
    assessment_center = '评估中心'
    system_admin = '系统管理员'


# 流程状态类型
class HuiXin_PROCESS_STATUS(Enum):
    RUNNING = "进行中"
    FINISHED = '已完成'
    AUDIT = '审核中'
    PASS = '通过'

# 只保留一处 __all__ 定义
__all__ = [
    'Assessment',
    'Process',
    'ProcessNode',
    'ProcessStepStatus',
    'HUIXIN_USER',
    'HuiXin_PROCESS_STATUS'
]
