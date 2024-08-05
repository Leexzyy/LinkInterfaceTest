import pymongo
from utils import my_utils,env_utils
import get_path_info

def connect_to_db():
    """
    连接到数据库，返回一个客户端对象。
    """
    env_tool = my_utils.get_env_tools()
    if my_utils.get_env() != 'TEST':
        mongo_client_url = env_tool.get_value('PRO_MONGO_CLIENT')
        print('数据库链接环境：PRO')
    else:
        mongo_client_url = env_tool.get_value('TEST_MONGO_CLIENT')
        print('数据库链接环境：TEST')


    client = pymongo.MongoClient(mongo_client_url)

    return client


def get_collection(database_name, collection_name):
    """
    从给定的数据库名称和集合名称获取一个数据库集合对象。
    """
    client = connect_to_db()
    db = client[database_name]
    collection = db[collection_name]
    return collection


def insert_document(database_name, collection_name, document):
    """
    将一个文档插入给定的集合中。

    参数：
        - database_name: 数据库名称。
        - collection_name: 集合名称。
        - document: 要插入的文档。
    """
    collection = get_collection(database_name, collection_name)
    collection.insert_one(document)


def find_documents(database_name, collection_name, query=None, limit=0):
    """
    根据给定的查询条件在集合中查找文档，并返回结果。

    参数：
        - database_name: 数据库名称。
        - collection_name: 集合名称。
        - query: 查询条件。默认为None，表示返回集合中的所有文档。
        - limit: 最大返回文档数。默认为0，表示返回所有匹配的文档。

    返回：
        返回一个游标，该游标包含符合查询条件的文档。
    """
    collection = get_collection(database_name, collection_name)
    cursor = collection.find(filter=query)
    if limit > 0:
        cursor.limit(limit)
    return cursor


def update_document(database_name, collection_name, query, update):
    """
    根据给定的查询条件和更新内容，在集合中更新文档。

    参数：
        - database_name: 数据库名称。
        - collection_name: 集合名称。
        - query: 查询条件。
        - update: 更新内容。

    返回：
        返回一个表示更新结果的字典。
    """
    collection = get_collection(database_name, collection_name)
    result = collection.update_many(query, update)
    return result.modified_count


def delete_document(database_name, collection_name, query):
    """
    根据给定的查询条件，在集合中删除文档。

    参数：
        - database_name: 数据库名称。
        - collection_name: 集合名称。
        - query: 查询条件。

    返回：
        返回一个表示删除结果的字典。
    """
    collection = get_collection(database_name, collection_name)
    result = collection.delete_many(query)
    return result.deleted_count


if __name__ == '__main__':
    # 定义数据库名称和集合名称
    database_name = "saturnbird"
    collection_name = "Order"
    # 调用工具类中的update_document函数执行更新操作
    result = find_documents('saturnbird', '_User', {'mobilePhoneNumber': '18597940021'})
    for i in result:
        print(i)

