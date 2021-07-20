import matplotlib.pyplot as plt
import numpy as np


plt.rcParams['figure.figsize'] = [10, 5]

def draw_bar_chart(x, y, title, x_label, y_label, filename='foo'):
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.bar(range(len(y)), y, tick_label=x)

    offset_y = max(y) * 0.01
    offset_x = len(x) * 0.025

    for i, v in enumerate(y):
        ax.text(i - offset_x, v + offset_y, str(v))

    plt.savefig(filename + ".png")


def draw_multibar_chart(X, Y, x_label, y_label, title=None, filename='foo'):
    fig, ax = plt.subplots()
    if title != None:
        ax.title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    width = 0.1
    x = np.arange(len(X))

    for i in range(len(Y)):
        y = Y[i]
        ax.bar(x + i*width, y, width, label=X[i])

    ax.set_xticks(x + width*len(x) / 2)
    ax.set_xticklabels(X)
    ax.legend()
    plt.savefig(filename + ".png")
