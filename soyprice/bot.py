#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twython import Twython, TwythonError
import datetime
from scraper import get_prices, get_chicago_price, get_days, get_next_workable_day, date_to_int, get_dollars
from statistic import forecast
import pylab as pl
from PIL import Image
from StringIO import StringIO
import numpy as np
import database as db



APP_KEY = 'rogbcg4oUIEHGh35kxMVGAf2k'
APP_SECRET = 'skkBp744JPEAXDnz0O3ZgxPX4qOpGU4Ao7rW588w1FTx4Laax4'
OAUTH_TOKEN = '282317077-WksqawGHtDE7ROc02ptId5Uei22hWEpnUe8NmGY9'
OAUTH_TOKEN_SECRET = 'ZaXiSkd4KIEiL7gf8OK63i4BteILTQKDaCNNOC5jhYHtm'
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)


def tweet(status, image):
    photo = open(image, 'rb')
    template = "%s [https://github.com/limiear/soyprice]"
    twitter.update_status_with_media(media=photo, status=template % status)


def graph(x, y, fix, next_x, next_y, dollars, fix_d, next_d_x, next_d_y, rmse, weights):
    data = filter(lambda d: d[1], zip(x, y))
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


def step():
    cache = db.open()
    try:
        amount = 30
        date_list = get_days(datetime.datetime.today(), range(0, amount))
	date_list.reverse()
        day = get_next_workable_day(date_list[-1])
	next_x = date_to_int(day)
        # dollars
        dollars = get_dollars(cache, date_list)
        params = zip(*dollars) + [next_x]
        price_d, rmse_d, fix_d, fx_d, weights = forecast(*params)
        # soy
        afascl = get_prices(cache, date_list)
        chicago = get_chicago_price(cache, date_list)
        params = zip(*afascl) + [next_x]
        price, rmse, fix, fx, weights = forecast(*params)
        print price_d
        params = zip(*afascl) + [fix , next_x , fx(next_x), dollars,
                                 fix_d, next_x, price_d, rmse, weights]
        filename = graph(*params)
        tweet(('Forecast Soja puerto San Martín con descarga para el'
               ' %s: AR$ %.f (RMSE: AR$ %i)') %
                (day.strftime('%d-%m-%Y'), price, int(rmse)),
               filename)
    except TwythonError as e:
        pass
    db.close(cache)

step()
