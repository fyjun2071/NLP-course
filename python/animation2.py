import random
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

matplotlib.use('Qt5Agg')


def init():
    ax.set_xlim(0, 2000)
    ax.set_ylim(-100, 100)
    x.append(0)
    y.append(random.random() * 200 - 100)
    line.set_data(x, y)
    return line,


def update(frame):
    x.append(frame)
    y.append(random.random() * 200 - 100)
    line.set_data(x, y)
    return line,


fig, ax = plt.subplots()
x, y = [], []
line, = ax.plot(x, y, '.')
ani = animation.FuncAnimation(fig, update, frames=range(2000), init_func=init, blit=True, interval=10, repeat=False)
plt.show()
