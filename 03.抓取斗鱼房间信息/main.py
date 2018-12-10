import requests
import pymongo

def douyu_spider():
    """
    先获取每个栏目的地址，再获取每个房间的信息
    """
    # 获取栏目地址
    game_sort_url = "http://open.douyucdn.cn/api/RoomApi/game"
    game_sort = requests.get(game_sort_url).json()["data"]  # 游戏分类信息 list
    game = []  # 游戏分类API地址
    pre_url = "http://api.douyutv.com/api/v1/live/"

    for item in game_sort:
        game.append(pre_url + item["short_name"])

    # 创建数据库链接
    conn = pymongo.MongoClient(host="localhost", port=27017)
    db = conn["douyu"]
    col = db["room_info"]

    # 获取房间信息
    print("开始抓取信息.......")
    for url in game:
        room_info_list = requests.get(url).json()["data"]
        for room in  room_info_list:
            data = {
                "room_id": room["room_id"],
                "room_name": room["room_name"],
                "nick_name": room["nickname"],
                "game_name": room["game_name"],
                "fans": room["fans"]
            }
            # 写入数据库
            try:
                col.insert(data)
            except Exception as e:
                print(e)
    print("抓取完成")


if __name__ == '__main__':
    douyu_spider()