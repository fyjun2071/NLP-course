"""
以1为中心无限螺旋递增数字，以给定的一个数字n开始，上下左右移动，
找到移动的中心点1的最短步数steps
    17 16 15 14 13
    18  5  4  3 12
    19  6  1  2 11
    20  7  8  9 10
    21 22 23---> …

例如：n=1, steps=0
    n=12, steps=3 下左左
    n=23, steps=2 下下
    n=1024, steps=31

思路：以中心1为第0圈，找出第i圈的最大数max(i)，可以确定指定数n在第几圈(k)
"""


def spiral_memory(n):
    k = 0
    max_num = 1
    # 找到n所在的圈及此圈最大值
    while True:
        max_num += 8 * k
        if max_num >= n:
            break
        k += 1
    if k == 0:
        return 0
    # 计算距离
    mod = (max_num - n) % (2 * k)
    if mod < k:
        return 2 * k - mod
    else:
        return mod


print(spiral_memory(1))
print(spiral_memory(12))
print(spiral_memory(23))
print(spiral_memory(1024))
print(spiral_memory(100000))
print(spiral_memory(2345678))
