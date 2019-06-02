def find(n):
    arr = [2, 3, 5]
    res = []
    for i in arr:
        mod = n % i
        while mod == 0:
            n //= i
            res.append(i)
            mod = n % i
    if len(res) == 0 or n != 1:
        return None
    else:
        return tuple(res)


print(find(6))
print(find(8))
print(find(14))
print(find(1845281250))
print(find(3690562500))
print(find(1230187500))
print(find(10023750))
