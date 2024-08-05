import os
from dotenv import dotenv_values, set_key


class EnvTool:
    def __init__(self, filepath):
        self.filepath = filepath

    def read_env(self):
        """
        读取.env文件，并返回一个包含键值对的字典
        """
        return dotenv_values(self.filepath)

    def get_value(self, key):
        """
        读取.env文件中指定键的值
        """
        env_content = self.read_env()
        return env_content.get(key)

    def write_to_env_file(self, env_content):
        with open(self.filepath, 'r') as file:
            lines = file.readlines()

        with open(self.filepath, 'w') as file:
            for key, value in env_content.items():
                updated = False
                for i in range(len(lines)):
                    if lines[i].startswith(key + '='):
                        file.write(key + "=" + value + '\n')  # 写入更新的内容
                        updated = True
                    else:
                        file.write(lines[i])  # 保持原有内容不变
                if not updated:
                    file.write(key + "=" + value + '\n')  # 如果原有内容中不存在该键值对，则添加新内容

    def update_env(self, key, value):
        """
        修改.env文件和系统环境变量中指定键的值，并保存修改
        """
        env_content = self.read_env()
        env_content[key] = value  # 更新.env文件内容
        self.write_to_env_file({key: value})  # 保存更新后的.env文件
        os.environ[key] = value  # 更新系统环境变量
        return self.get_value(key)  # 返回更新后的值


# 测试示例
if __name__ == '__main__':
    from InterfaceTest.OrderPaymentTest import get_path_info

    path = get_path_info.get_path()
    # 创建EnvTool实例
    env_tool = EnvTool(f'{path}/payment.env')

    # 读取.env文件
    env_content_before = env_tool.read_env()
    print("读取.env文件内容：", env_content_before)

    # 读取指定键的值
    value = env_tool.get_value('DEBUG_Model')
    print("DEBUG_Model的值：", value)

    # 修改.env文件中的某个键值对
    env_content_after = env_tool.update_env('DEBUG_Model', 'new_value')
    print("修改后的.env文件内容：", env_content_after)
    # 读取指定键的值
    value = env_tool.get_value('DEBUG_Model')
    print("DEBUG_Model的值：", value)
