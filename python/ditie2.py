import requests
from bs4 import BeautifulSoup

# 北京地铁时间信息
time_info_url = 'http://www.bjsubway.com/e/action/ListInfo/?classid=39&ph=1'
# 北京地铁距离信息
distance_info_url = 'http://www.bjsubway.com/station/zjgls/'
# 两站之间连接的信息: {hash(name1)+hash(name2):Connection}
p2p_map = {}
# 与相邻站的连接: {name:{next1, next2, ...}}
connection_map = {}


def get_hash(name1, name2):
    return hash(name1) + hash(name2)


class Connection:
    """
    两站之间连接的信息
    name1: 第一站名称
    name2: 第二站名称
    diff_time: 两站之间所需时间，分钟
    distance: 两站之间的距离，米
    """

    def __init__(self, name1, name2):
        self.name1 = name1
        self.name2 = name2
        self.diff_time = None
        self.distance = None

    def __hash__(self):
        return get_hash(self.name1, self.name2)

    def __str__(self):
        return "{}-{}:{},{}".format(self.name1, self.name2, self.diff_time, self.distance)

    def __eq__(self, other):
        return self.__hash__() == other.hash()

    def hash(self):
        return self.__hash__()

    def next(self, name):
        if name == self.name1:
            return self.name2
        else:
            return self.name1


def add_connection(name1, name2):
    if name1 in connection_map:
        connection_map[name1].add(name2)
    else:
        connection_map[name1] = {name2}


def get_connection(name1, name2):
    key = get_hash(name1, name2)
    if key in p2p_map:
        return p2p_map[key]
    else:
        return None


def parse_time_table(table_data):
    """
    解析站间时间
    """

    def parse_time(string):
        split = string.split(':')
        if len(split) == 2:
            return int(split[0]) * 60 + int(split[1])
        else:
            return None

    def build_time_connection(row1, row2):
        if len(row1) != len(row2):
            return
        name = row1[0]
        next_name = row2[0]
        diff_time = None
        for j in range(1, min(len(row1), len(row2))):
            time = parse_time(row1[j])
            next_time = parse_time(row2[j])
            if time and next_time:
                diff_time = abs(time - next_time)
                if diff_time > 10:  # 时间太长，不要
                    diff_time = None
                    continue
                break
        conn = Connection(name, next_name)
        if conn.hash() in p2p_map:
            p2p_map[conn.hash()].diff_time = diff_time
        else:
            conn.diff_time = diff_time
            p2p_map[conn.hash()] = conn
        add_connection(conn.name1, conn.name2)
        add_connection(conn.name2, conn.name1)

    for i, row in enumerate(table_data):
        if i > 0:
            build_time_connection(row, table_data[i - 1])
        if i < len(table_data) - 1:
            build_time_connection(row, table_data[i + 1])


def init_connection_time():
    """
    获取站间时间信息
    """
    response = requests.get(time_info_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    for table in tables:
        table_data = []
        for tr in table.find_all('tr'):
            row = []
            for td in tr.find_all(['th', 'td']):
                text = td.getText().strip()
                if text == '生物医院基地':  # 4号线名称标错了
                    text = '生物医药基地'
                row.append(text)
            table_data.append(row)
        parse_time_table(table_data[3:])


def parse_distance_table(table_data):
    """
    解析站间的距离
    """
    for row in table_data:
        split = row[0].split('――')
        name1 = split[0]
        name2 = split[1]
        distance = int(row[1])
        conn = Connection(name1, name2)
        if conn.hash() in p2p_map:
            p2p_map[conn.hash()].distance = distance
        else:
            conn.distance = distance
            p2p_map[conn.hash()] = conn
        add_connection(conn.name1, conn.name2)
        add_connection(conn.name2, conn.name1)


def init_connection_distance():
    """
    获取站间距离信息
    """
    response = requests.get(distance_info_url)
    response.encoding = 'gb2312'
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    for table in tables:
        table_data = []
        for tr in table.find_all('tr'):
            row = []
            for td in tr.find_all(['th', 'td']):
                row.append(td.getText().strip())
            table_data.append(row)
        parse_distance_table([row[:2] for row in table_data[2:]])


def search(start, destination, connection_grpah, sort_candidate):
    """
    广度优先搜索，获取最优路径
    """
    pathes = [[start]]
    visitied = set()
    while pathes:
        path = pathes.pop(0)
        froninter = path[-1]
        if froninter in visitied: continue
        successors = connection_grpah[froninter]
        for city in successors:
            if city in path: continue
            new_path = path + [city]
            pathes.append(new_path)
            if city == destination:
                return new_path
        visitied.add(froninter)
        pathes = sort_candidate(pathes)


def transfer_stations_first(pathes):
    """
    最少换乘优先
    """
    return sorted(pathes, key=len)


def transfer_time_fisrt(pathes):
    """
    最短时间优先
    """
    if len(pathes) <= 1:
        return pathes

    def sum_time(path):
        time = 0
        for i in range(len(path) - 1):
            conn = get_connection(path[i], path[i + 1])
            if conn.diff_time:
                time += conn.diff_time
            else:
                time += avg_diff_time  # 没有时间则使用平均时间
        return time

    return sorted(pathes, key=sum_time)


def transfer_distance_fisrt(pathes):
    """
    最短距离优先
    """
    if len(pathes) <= 1:
        return pathes

    def sum_distance(path):
        distance = 0
        for i in range(len(path) - 1):
            conn = get_connection(path[i], path[i + 1])
            if conn.distance:
                distance += conn.distance
            else:
                distance += avg_distance  # 没有距离则使用平均距离
        return distance

    return sorted(pathes, key=sum_distance)


init_connection_time()
init_connection_distance()
# 平均时间
diff_time_list = [c.diff_time for c in p2p_map.values() if c.diff_time]
avg_diff_time = round(sum(diff_time_list) / len(diff_time_list), 0)
# 平均距离
distance_list = [c.distance for c in p2p_map.values() if c.distance]
avg_distance = round(sum(distance_list) / len(distance_list), 0)
path = search('西直门', '国贸', connection_map, sort_candidate=transfer_time_fisrt)
print(path)
