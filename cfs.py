#!/usr/bin/env python3

"""
Program to simulate Completely Fair Scheduler (CFS).
"""

import random
import sys
from math import floor
from typing import Callable, List

import numpy
from sortedcontainers import SortedKeyList
from tabulate import tabulate

from weight import weightMapper 
# import sched_algs
import logging
from logger import create_logger

def cfs_schedule(tasks: List[dict], quantum: int, totalSumOfWeight: int, logger):
    """
    Schedule tasks according to CFS algorithm and set waiting and turnaround times.
    """
    # its return can be call(callable), if it return false , it means it will can't not be call absolutely.

    get_vruntime: Callable[[dict], int] = lambda task: task["vruntime"]
    get_nice: Callable[[dict], int] = lambda task: task["nice"]

    tasks_sorted = SortedKeyList(key=get_vruntime) #sort as task's vruntime
    # tasks were Sorted by arrival time
    tasks_sorted.add(tasks[0]) # 找出最先抵達的task
    end = 1
    # timer = tasks[0]["arrival_time"]
    timer = 0
    min_vruntime = 0
    # curTime = 0
    while (num := len(tasks_sorted)) > 0:
        logger.debug(('current timer:',timer))
        total_weight_iter = 0
        vruntime = 0
        # Add tasks that have arrived after previous iteration
        #從最後面(抵達時間最晚)開始加到tasks_sorted內
        for task in tasks[end:]:
            # 如果最先抵達的任務的時間 小於目前的時間軸時間 代表此任務已抵達
            # >就加到task_s內 一起被執行
            if task["arrival_time"] <= timer:
                task["waiting_time"] = timer - task["arrival_time"]
                task["turnaround_time"] = task["waiting_time"]
                task["vruntime"] = min_vruntime #初始設定為0
                tasks_sorted.add(task)
                num += 1
                end += 1
        
        for task_this_iteration in tasks_sorted:
            total_weight_iter += task_this_iteration["weight"]



        # timeslice = floor(quantum / num)  # Dynamic timeslice
        timeslice = quantum #6ms
        min_task = tasks_sorted[0] #最早抵達的那個

        # Time remaining for smallest task
        t_rem = min_task["burst_time"] - min_task["exec_time"]

        #min_granularity 0.75 ms
        if t_rem <= 750:
            t_rem = 750

        # Time of execution of smallest task
        # calculate the corresponding execution time
        # in this time slice
        # time = min([timeslice, t_rem])
        #計算時要考慮剩餘時間
        logger.debug(('the weight :',str(min_task["weight"]),
        'total_weight_iter:',str(total_weight_iter)))
        logger.debug(('ratio :',str(min_task["weight"] / total_weight_iter))) 



        time = min([timeslice *  min_task["weight"] / total_weight_iter, t_rem])
        #> the execution of single task should base on its weight of total weight
        min_vruntime = time * 1024 / min_task["weight"]
        logger.debug(('execute time of tasks:',str(time),'t_rem:',str(t_rem),
        'vruntime of the task:',str(min_vruntime)))
        # min_vruntime = get_vruntime(min_task) #一開始是0
        min_nice = get_nice(min_task) 

        # display_tasks(tasks_sorted)
        logger.debug(f'Executing task {min_task["pid"]} for {time} ms\n')

        # Execute process
        # vruntime = min_vruntime + time * min_nice
        vruntime = vruntime + min_vruntime  #update vruntime
        
        min_task["exec_time"] += time
        min_task["turnaround_time"] += time
        timer += time #更新現在時間 

        # Increment waiting and turnaround time of all other processes
        for i in range(1, num):
            tasks_sorted[i]["waiting_time"] += time
            tasks_sorted[i]["turnaround_time"] += time

        # Remove from sorted list and update vruntime
        task = tasks_sorted.pop(0)
        task["vruntime"] = task["vruntime"] + vruntime  #update vruntime
        logger.debug(('updating vruntime:',task["vruntime"]))

        # Insert only if execution time is left
        if min_task["exec_time"] < min_task["burst_time"]:
            tasks_sorted.add(task)


def display_tasks(tasks: List[dict]):
    """
    Print all tasks' information in a table.
    """

    headers = [
        "ID",
        "Arrival Time",
        "Burst Time",
        "Nice",
        "Waiting Time",
        "Turnaround Time",
    ]
    tasks_mat = []

    for task in tasks:
        tasks_mat.append(
            [
                task["pid"],
                f"{task['arrival_time'] / 1000}",
                f"{task['burst_time'] / 1000}",
                task["nice"],
                f"{task['waiting_time'] / 1000}",
                f"{task['turnaround_time'] / 1000}",
            ]
        )
    print(
        "\n"
        + tabulate(tasks_mat, headers=headers, tablefmt="fancy_grid", floatfmt=".3f")
    )
    # print('\n' + tabulate(tasks, headers='keys', tablefmt='fancy_grid'))


def find_avg_time(tasks: List[dict]):
    """
    Find average waiting and turnaround time.
    """

    waiting_times = []
    total_wt = 0
    total_tat = 0
    num = len(tasks)

    for task in tasks:
        waiting_times.append(task["waiting_time"])
        total_wt += task["waiting_time"]
        total_tat += task["turnaround_time"]

    print(f"\nAverage waiting time: {total_wt / (num * 1000): .3f} seconds")
    print(f"Average turnaround time: {total_tat / (num * 1000): .3f} seconds")
    print(
        "Standard deviation in waiting time: "
        f"{numpy.std(waiting_times) / 1000: .3f} seconds"
    )


def reset_tasks(tasks: List[dict]):
    """
    Reset task execution details.
    """

    for task in tasks:
        task["vruntime"] = 0
        task["exec_time"] = 0
        task["waiting_time"] = 0
        task["turnaround_time"] = 0


if __name__ == "__main__":
    logger = create_logger('test')
    MIN_VERSION = (3, 8)
    if not sys.version_info >= MIN_VERSION:
        raise EnvironmentError(
            "Python version too low, required at least "
            f'{".".join(str(n) for n in MIN_VERSION)}'
        )
    logging.basicConfig(level = logging.INFO)
    QUANTUM = 6  # sysctl_sched_latency 
    MAX_ARRIVAL_TIME = 20_000
    MAX_BURST_TIME = 50_000
    MAX_NICE_VALUE = 20

    N = int(input("Enter number of tasks: "))
    TASKS = []

    print('Enter ID, arrival time, burst time, nice value of processes:')
    print('(Times should be in milliseconds)')
    totalSumOfWeight = 0
    for _ in range(N):
        pid, at, bt, nice = tuple(int(x) for x in input().split())
        # pid, at, bt, nice = (
        #     random.randint(1, N * N),
        #     random.randint(0, MAX_ARRIVAL_TIME),
        #     random.randint(0, MAX_BURST_TIME),
        #     random.randint(1, MAX_NICE_VALUE),
        # )
        TASKS.append(
            {
                "pid": pid,
                "arrival_time": at,
                "burst_time": bt,
                "nice": nice,
                "vruntime": 0,
                "exec_time": 0,
                "waiting_time": 0,
                "turnaround_time": 0,
                "weight":weightMapper(str(nice))
            }
        )
        totalSumOfWeight += weightMapper(str(nice))

    logger.info('totalSumOfWeight:',totalSumOfWeight)
    # Sort tasks by arrival time
    TASKS_SORTED = SortedKeyList(TASKS, key=lambda task: task["arrival_time"])

    # Schedule tasks according to CFS algorithm and print average times
    reset_tasks(TASKS_SORTED)
    cfs_schedule(TASKS_SORTED, QUANTUM, totalSumOfWeight,logger)
    print("\n**************** CFS SCHEDULING ****************")
    display_tasks(TASKS)
    find_avg_time(TASKS)

    # # Schedule tasks according to FCFS algorithm and print average times
    # reset_tasks(TASKS_SORTED)
    # sched_algs.fcfs_schedule(TASKS_SORTED)
    # print("\n**************** FCFS SCHEDULING ****************")
    # # display_tasks(TASKS)
    # find_avg_time(TASKS)

    # # Schedule tasks according to SJF algorithm and print average times
    # reset_tasks(TASKS_SORTED)
    # sched_algs.sjf_schedule(TASKS_SORTED, QUANTUM)
    # print("\n**************** SJF SCHEDULING ****************")
    # # display_tasks(TASKS)
    # find_avg_time(TASKS)

    # # Schedule tasks according to priority algorithm and print average times
    # reset_tasks(TASKS_SORTED)
    # sched_algs.priority_schedule(TASKS_SORTED, QUANTUM)
    # print("\n**************** PRIORITY SCHEDULING ****************")
    # # display_tasks(TASKS)
    # find_avg_time(TASKS)

    # # Schedule tasks according to round robin algorithm and print average times
    # reset_tasks(TASKS_SORTED)
    # sched_algs.rr_schedule(TASKS_SORTED, QUANTUM)
    # print("\n**************** ROUND ROBIN SCHEDULING ****************")
    # # display_tasks(TASKS)
    # find_avg_time(TASKS)
