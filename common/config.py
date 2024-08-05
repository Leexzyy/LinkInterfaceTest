from utils import env_utils
import get_path_info

path = get_path_info.get_path()
env_tool = env_utils.EnvTool(f'{path}/payment.env')
# 工程配置文件 必改！！！！！！
REPORT_NAME = 'Payment_Report'
REPORT_TITLE = '支付自动化接口测试报告'
PROJECT_NAME = 'payment'

# ENV = 'TEST'

# 测试环境地址
BASE_TEST_URL = env_tool.get_value('BASE_TEST_URL')
BASE_TEST_PAY_HOOK = env_tool.get_value('BASE_TEST_PAY_HOOK')

# OSS配置
OSS_PATH = 'auto-test-pay'


# 接口状态
STATUS_CODE = 200

# 接口状态
INTERFACE_STATUS = {
    'SUCCESS': 200,
    'ERROR': 500,
    'NOT_FOUND': 404,
    'FORBIDDEN': 403,
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'NOT_IMPLEMENTED': 501,
    'SERVICE_UNAVAILABLE': 503}
# 接口响应时间
INTERFACE_TIME_OUT = 10

# 测试请求头
TEST_HEADERS = {
    'x-lc-sign': env_tool.get_value('TEST_SIGN'),
    'x-lc-session': env_tool.get_value('TEST_TOKEN'),
    'x-lc-id': env_tool.get_value('TEST_LC_ID')
}

# 生产请求头
PRO_HEADERS = {
    'x-lc-sign': env_tool.get_value('PRO_SIGN'),
    'x-lc-session': env_tool.get_value('PRO_TOKEN'),
    'x-lc-id': env_tool.get_value('PRO_LC_ID')
}

# 测试管理端 cookies
TEST_ADMIN_COOKIES = {'b-user-id': env_tool.get_value('TEST_ADMIN_B_USER_ID'),
                 'stbird': env_tool.get_value('TEST_STBIRD'),
                 'stbird.sig': env_tool.get_value('TEST_STBIRD.SIG')}
# 管理端 headers
TEST_ADMIN_HEADERS = {
    'x-lc-id': env_tool.get_value('TEST_ADMIN_ID'),
    'x-lc-session': env_tool.get_value('TEST_ADMIN_SESSION'),
    'x-lc-sign': env_tool.get_value('TEST_ADMIN_SIGN'),
}
# 生产管理端 headers
PRO_ADMIN_HEADERS = {
    'x-lc-id': env_tool.get_value('PRO_ADMIN_ID'),
    'x-lc-session': env_tool.get_value('PRO_ADMIN_SESSION'),
    'x-lc-sign': env_tool.get_value('PRO_ADMIN_SIGN'),
}


