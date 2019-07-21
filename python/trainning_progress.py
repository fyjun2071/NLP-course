import random
from sklearn.datasets import load_boston
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

matplotlib.use('Qt5Agg')

data = load_boston()
X, y = data['data'], data['target']
X_rm = X[:, 5]

min_loss = float('inf')
current_k = random.random() * 200 - 100
current_b = random.random() * 200 - 100
learning_rate = 1e-04


def draw_rm_and_price():
    plt.scatter(X_rm, y)


def draw_result(k, b):
    print('k: {}, b: {}'.format(k, b))
    price_by_random_k_and_b = [price(r, k, b) for r in X_rm]
    draw_rm_and_price()
    plt.scatter(X_rm, price_by_random_k_and_b)


def price(rm, k, b):
    """f(x) = k * x + b"""
    return k * rm + b


def loss(y, y_hat):
    return sum((y_i - y_hat_i) ** 2 for y_i, y_hat_i in zip(list(y), list(y_hat))) / len(list(y))


def partial_k(x, y, y_hat):
    return -2 / len(y) * sum([(y_i - y_hat_i) * x_i for x_i, y_i, y_hat_i in zip(list(x), list(y), list(y_hat))])


def partial_b(x, y, y_hat):
    return -2 / len(y) * sum([y_i - y_hat_i for y_i, y_hat_i in zip(list(y), list(y_hat))])


def init():
    price_by_k_and_b = [price(r, current_k, current_b) for r in X_rm]
    current_loss = loss(y, price_by_k_and_b)
    ax.set_xlim(0, 2000)
    ax.set_ylim(0, current_loss + 10)
    x_data.append(0)
    y_data.append(current_loss)
    line.set_data(x_data, y_data)
    return line,


def update(frame):
    global min_loss
    global current_k
    global current_b
    price_by_k_and_b = [price(r, current_k, current_b) for r in X_rm]
    current_loss = loss(y, price_by_k_and_b)
    k_gradient = partial_k(X_rm, y, price_by_k_and_b)
    b_gradient = partial_b(X_rm, y, price_by_k_and_b)
    current_k = current_k + (-1 * k_gradient) * learning_rate
    current_b = current_b + (-1 * b_gradient) * learning_rate
    x_data.append(frame)
    y_data.append(current_loss)
    print(frame, current_loss)
    line.set_data(x_data, y_data)
    return line,


fig, ax = plt.subplots()
x_data, y_data = [], []
line, = ax.plot(x_data, y_data)
ani = animation.FuncAnimation(fig, update, frames=range(1, 2000), init_func=init, blit=True)
plt.show()
