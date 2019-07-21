import re
import requests
from bs4 import BeautifulSoup

base_url = 'http://bj.bendibao.com'
# 两站之间连接的信息: {hash(name1)+hash(name2):Connection}
p2p_map = {}
# 与相邻站的连接: {name:{next1, next2, ...}}
connection_map = {}


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
        return hash(self.name1) + hash(self.name2)

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


def get_station_time(href):
    soup = BeautifulSoup(requests.get(base_url + href).text, 'html.parser')
    table = []
    for tr in soup.table.find_all('tr'):
        row = []
        for td in tr.find_all('td'):
            row.append(td.getText())
        table.append(row)
    return [row[::2] for row in table[2:]]


def parse_time_table(table):
    def parse_time(string):
        split = string.split(':')
        if len(split) == 2:
            return int(split[0]) * 60 + int(split[1])
        else:
            return None

    def build_time_connection(row1, row2):
        name = row1[0]
        time = parse_time(row1[1])
        time_backup = parse_time(row1[2])
        next_name = row2[0]
        next_time = parse_time(row2[1])
        next_time_backup = parse_time(row2[2])
        if time and next_time:
            diff_time = abs(time - next_time)
        elif time_backup and next_time_backup:
            diff_time = abs(time_backup - next_time_backup)
        else:
            diff_time = 2
        conn = Connection(name, next_name)
        conn.diff_time = diff_time
        return conn

    def add_connection(name1, name2):
        if name1 in connection_map:
            connection_map[name1].add(name2)
        else:
            connection_map[name1] = {name2}

    for i, row in enumerate(table):
        conn = None
        if i > 0:
            conn = build_time_connection(row, table[i - 1])
        if i < len(table) - 1:
            conn = build_time_connection(row, table[i + 1])
        if conn:
            p2p_map[conn.hash()] = conn
            add_connection(conn.name1, conn.name2)
            add_connection(conn.name2, conn.name1)


def get_station_distance(href):
    response = requests.get(base_url + href)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    table = []
    for tr in soup.find(id='bo').table.find_all('tr'):
        row = []
        for td in tr.children:
            row.append(td.getText())
        table.append(row)
    return [row[:2] for row in table[2:]]


def parse_distance_table(table):
    tmp_connecton_map = {}
    for row in table:
        split = row[0].split('——')
        name1 = split[0]
        name2 = split[1]
        distance = int(row[1])
        conn = Connection(name1, name2)
        if conn.hash() in p2p_map:
            p2p_map[conn.hash()].distance = distance
        else:
            conn.distance = distance
            tmp_connecton_map[conn.hash()] = conn
            p2p_map[conn.hash()] = conn


def init_connection_time():
    response = requests.get(base_url + '/ditie/linemap.shtml')
    soup = BeautifulSoup(response.text, 'html.parser')
    station_time_href = [a.get('href') for a in soup.select('div .m.m-3')[0].select('li a')]
    for href in station_time_href:
        parse_time_table(get_station_time(href))


def init_connection_distance():
    response = requests.get(base_url + '/traffic/20141217/174547.shtm')
    pattern = re.compile(r'<a target="_blank" href="http://bj\.bendibao\.com(/traffic/\d+/\d+.shtm)">')
    for href in pattern.findall(response.text):
        parse_distance_table(get_station_distance(href))


# parse_distance_table(get_station_distance('/traffic/20141217/174547.shtm'))
init_connection_time()
init_connection_distance()
for k, v in p2p_map.items():
    if not v.diff_time or not v.distance:
        print(k, v)
# for k, v in connection_map.items():
#     print(k, v)