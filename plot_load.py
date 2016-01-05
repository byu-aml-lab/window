#!/usr/bin/env python3

"""Real time plot of potato loads"""

import collections
import datetime
import matplotlib
import matplotlib.dates as dates
import matplotlib.pyplot as plt
import re
import seaborn
import subprocess
import time

def get_loads():
    """Gets the loads of the potatoes as a list"""
    cmd = ['pssh', '-i', '-h', '/config/potatoes/all', 'uptime']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = process.communicate()[0].decode('utf-8')
    output = re.findall(r'\d+potato.*\n.+$', output, re.MULTILINE)
    return [parse_load(line) for line in sorted(output)]


def parse_load(line):
    """Parses the load from a line of uptime output"""
    if 'load average' in line:
        samples = [float(val.replace(',', '')) for val in line.split()[-3:]]
        return sum(samples) / len(samples)
    else:
        return 0


def run_plot(num_pts=100, maximize=False, interval_secs=5, xaxis_fmt='%I:%M'):
    """Runs the interactive plot of potato load"""
    matplotlib.rcParams['toolbar'] = 'None'
    if maximize:
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
    plt.gcf().canvas.set_window_title(' ')
    plt.xkcd()
    plt.ion()
    plt.show()

    data = [collections.deque([load], num_pts) for load in get_loads()]
    times = collections.deque([datetime.datetime.now()], num_pts)

    seaborn.set_palette('Set2', len(data))

    while True:
        for loads, new_load in zip(data, get_loads()):
            loads.append(new_load)
        times.append(datetime.datetime.now())

        plt.clf()
        for loads in data:
            plt.plot(times, loads)

        plt.title('AML Lab Cluster Loads', fontsize=60)
        plt.gca().xaxis.set_major_formatter(dates.DateFormatter(xaxis_fmt))
        plt.draw()

        time.sleep(interval_secs)

if __name__ == '__main__':
    run_plot(1000, True, 30)
