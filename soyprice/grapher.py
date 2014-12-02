from scraper import date_to_int
import pylab as pl


def graph(variable, fix, next_x, next_y, dollars, fix_d, next_d_x, next_d_y, rmse, weights):
    data = filter(lambda d: d[1], variable)
    x, y = zip(*data)
    x = map(date_to_int, x)
    border = 2
    ratio = 100
    x_values = list(x) + [next_x]
    y_values = list(y) + [next_y]
    limits = (min(x_values) - border,
              max(x_values) + border,
              min(y_values) - border * ratio,
              max(y_values) + border * ratio)
    pl.figure(figsize=(8, 4), dpi=100)
    pl.title('Soja puerto San Martin por @limiear')
    ax = pl.subplot(1, 1, 1)
    ax.axis(limits)
    ax.scatter(x, y, marker=".", linewidth=0.5)
    w_s = lambda w: 1/(w if w > 0 else 0.001)
    ax.plot(x, map(lambda (x, w): x - (rmse * w_s(w)), zip(fix, weights)),
            color="green", linewidth=1.0, linestyle="--",)
    ax.plot(x, fix, color="red", linewidth=1.0, linestyle="-",)
    ax.plot(x, map(lambda (x, w): x + (rmse * w_s(w)), zip(fix, weights)),
            color="green", linewidth=1.0, linestyle="--",)
    ax.plot([next_x], [next_y], color="red", marker="o")
    pl.xticks([], 0, endpoint=True)
    pl.xlabel("ventana de %i dias previos" % (x[-1] + 1 - x[0]), fontsize=10)
    pl.ylabel('AR$', fontsize=10)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    # bx = pl.subplot(2, 1, 2)
    # bx.scatter(*zip(*dollars))
    # pl.plot(x, fix_d, color="red", linewidth=1.0, linestyle="-",)
    # pl.plot([next_d_x], [next_d_y], color="red", marker="o")
    # bx.yaxis.tick_right()
    # bx.yaxis.set_label_position("right")
    filename = "graph.png"
    pl.savefig(filename, dpi=100)
    return filename