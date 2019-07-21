import math
import random
import time
from functools import wraps
from functools import lru_cache
import matplotlib.pyplot as plt
import networkx as nx


def to_bit_map(length):
    """
    给定长度，转换成bitmap，从右向左
    :param length:
    :return:
    """
    return (1 << length) - 1


def bit_map_set(bm, i):
    """
    将bm第i位设为1
    :param bm:
    :param i:
    :return:
    """
    return bm | (1 << i)


def bit_map_clean(bm, i):
    """
    将bm第i位设为0
    :param bm:
    :param i:
    :return:
    """
    return bm & (~(1 << i))


def bit_map_has(bm, i):
    """
    检查bm第i位是否为1
    :param bm:
    :param i:
    :return:
    """
    return bool(bm & (1 << i))


def bit_map_all(bm):
    """
    获取所有为1的索引
    :param bm:
    :return:
    """
    return [i for i in range(len(str(bin(bm))[2:])) if bit_map_has(bm, i)]


def bit_map_str(bm, length=None):
    s = str(bin(bm))[2:]
    if not length:
        length = len(s)
    return '0' * (length - len(s)) + s


def distance(p1, p2):
    """
    计算两点距离
    :param p1: 数组points的索引
    :param p2: 数组points的索引
    :return:
    """
    return math.sqrt((points[p1][0] - points[p2][0]) ** 2 + (points[p1][1] - points[p2][1]) ** 2)


def cache_print(func):
    """
    计算函数耗时
    :param func:
    :return:
    """

    @wraps(func)
    def _warp(*args, **kwargs):
        key = tuple(args)
        if key in cache:
            num = cache[key] + 1
            cache[key] = num
            print(key, num)
        else:
            cache[key] = 1
        result = func(*args, **kwargs)
        return result

    return _warp


@lru_cache(maxsize=2 ** 30)
@cache_print
def search(p, bm):
    """
    搜索方案
    :param p:
    :param bm:
    :return:
    """
    rest = bit_map_all(bm)
    if len(rest) == 0:
        solution[(p, bm)] = p
        return distance(0, p)
    min_distance, index = min([(distance(p, i) + search(i, bit_map_clean(bm, i)), i) for i in rest], key=lambda x: x[0])
    solution[(p, bm)] = index
    return min_distance


def parse_solution(status, solution_map):
    """
    解析最优方案
    :param status:
    :param solution_map:
    :return:
    """
    if status[1] == 0:
        return []
    p = solution_map[status]
    return [p] + parse_solution((p, bit_map_clean(status[1], p)), solution_map)


def draw_solution(idx_path, points_coord):
    """
    画出路径
    :param idx_path: 路径连线，points的索引
    :param points_coord: 点的坐标列表
    :return:
    """
    location_map = {}
    for i, p in enumerate(points_coord):
        location_map[i] = p
    edges = [(idx_path[i - 1], idx_path[i]) for i in range(1, len(idx_path))]

    DG = nx.DiGraph()
    DG.add_edges_from(edges)
    nx.draw_networkx_nodes(DG, location_map)
    nx.draw_networkx_edges(DG, location_map, edge_color='r', arrows=True)
    nx.draw_networkx_labels(DG, location_map)
    plt.show()


def elapsed_time(func):
    """
    计算函数耗时
    :param func:
    :return:
    """

    @wraps(func)
    def _warp(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        name = func.__name__
        elapsed = time.time() - t0
        arg_lst = []
        if args:
            arg_lst.append(', '.join(repr(arg) for arg in args))
        if kwargs:
            pairs = ['%s=%r' % (k, w) for k, w in sorted(kwargs.items())]
            arg_lst.append(', '.join(pairs))
        arg_str = ', '.join(arg_lst)
        print('%s(%s) -> %r, elapsed time:%0.8fs' % (name, arg_str, result, elapsed))
        return result

    return _warp


@elapsed_time
def search_solution(n):
    """
    搜索最优路径
    :param n: 点的个数
    :return: 最优路径，点的索引列表
    """
    bitmap = to_bit_map(n)
    # 搜索路径
    search(0, bit_map_clean(bitmap, 0))
    # 解析路径
    return [0] + parse_solution((0, bit_map_clean(bitmap, 0)), solution) + [0]


latitudes = [random.randint(-100, 100) for _ in range(15)]
longitude = [random.randint(-100, 100) for _ in range(15)]
points = list(zip(latitudes, longitude))
print('points:', points)
solution = {}
cache = {}
path = search_solution(len(points))
draw_solution(path, points)
