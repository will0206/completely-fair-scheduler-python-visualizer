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
from datetime import datetime
import random
from matplotlib import pyplot as plt 

def cfsSchedule(tasks: List[dict], quantum: int, logger: object):

    xcood = []
    processes = [] #[[],[],[]]
    for i in range(0,len(tasks)):
        xcood.append([0.0])
        processes.append([0.0])

    # its return can be call(callable), if it return false , it means it will can't not be call absolutely.

    get_vruntime: Callable[[dict], int] = lambda task: task["vruntime"]
    get_nice: Callable[[dict], int] = lambda task: task["nice"]

    tasks_sorted = SortedKeyList(key=get_vruntime) #sort as task's vruntime
    # tasks were Sorted by arrival time
    tasks_sorted.add(tasks[0]) # 找出最先抵達的task
    end = 1
    timer = tasks[0]["arrival_time"]
    min_vruntime = 0

    processRuntime = {}
    listname = 'X axis'
    for t in tasks:
        processRuntime[str(t["pid"])] = 0
        listname = listname + ',' + 'process' + str(t["pid"])
    
    print(processRuntime)
    logger.debug(f'{listname}')
    
    while (num := len(tasks_sorted)) > 0:
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
        if t_rem <= 0.75:
            t_rem = 0.75

        # Time of execution of smallest task
        # calculate the corresponding execution time
        # in this time slice
        # time = min([timeslice, t_rem])
        #計算時要考慮剩餘時間
        # logger.debug(('the weight :',str(min_task["weight"]),
        # 'total_weight_iter:',str(total_weight_iter)))
        # logger.debug(('ratio :',str(min_task["weight"] / total_weight_iter))) 


        #execution time of the process
        time = min([timeslice *  min_task["weight"] / total_weight_iter, t_rem])
        #> the execution of single task should base on its weight of total weight
        min_vruntime = time * 1024 / min_task["weight"]

        # logger.debug(('execute time of tasks:',str(time),'t_rem:',str(t_rem),
        # 'vruntime of the task:',str(min_vruntime)))
        # min_vruntime = get_vruntime(min_task) #一開始是0
        min_nice = get_nice(min_task) 

        # display_tasks(tasks_sorted)
        # logger.debug(f'Executing task {min_task["pid"]} for {time} ms\n')

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
        task = tasks_sorted.pop(0) #

        
        task["vruntime"] = task["vruntime"] + vruntime  #update vruntime
        # logger.debug(f'{min_task["pid"]} vruntime update to : {task["vruntime"]}\n')


        # Insert only if execution time is left
        if min_task["exec_time"] < min_task["burst_time"]:
            tasks_sorted.add(task)

        # use to print
        nowExecutePid = str(min_task["pid"])
        processRuntime[nowExecutePid] = processRuntime[nowExecutePid] + time

        
        printlog(tasks,min_task,timer,processRuntime,logger)
        taskIndex = tasks.index(min_task) #0 1 2
        
        for i in range(0,len(processes)):
            if i != taskIndex and len(processes[i])>0:
                processes[i].append(processes[i][-1])
                xcood[i].append(timer)
            else:
                processes[taskIndex].append(processRuntime[str(min_task["pid"])])
                xcood[taskIndex].append(timer)

    drawResult(xcood,processes)    


def displayTasks(tasks: List[dict]):
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


def findAvgTime(tasks: List[dict]):
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


def initTasks(tasks: List[dict]):
    for task in tasks:
        task["vruntime"] = 0
        task["exec_time"] = 0
        task["waiting_time"] = 0
        task["turnaround_time"] = 0

def drawResult(xcood,processes):
    plt.title('CFS Result')  # 折线图标题
    plt.xlabel('time(ms)')  # x轴标题
    plt.ylabel('CPU burst time')  # y轴标题
    for i in processes[1]:
        print(i)
    # print('A:',processes[0],'\n')
    # print('B:',processes[1],'\n')
    # print('C:',processes[2],'\n')
    
    # plt.xticks([0,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000])
    
    for i in range(0,len(xcood)):
        plt.plot(xcood[i],processes[i],color=(random.randint(0,255)/255,random.randint(0,255)/255,random.randint(0,255)/255))

    plt.show()
    #x [1,2] [,] [,]
def printlog(tasks,min_task,timer,processRuntime,logger):
    taskIndex = tasks.index(min_task) #0 1 2
    log = str(timer)
    for i in range(0,len(tasks)):
        if i == taskIndex:
            log = log + ',' +str(processRuntime[str(min_task["pid"])])
        else:
            log = log + ','

    print(log)
    logger.debug(log)

def generateRandomProcess(N,MAX_ARRIVAL_TIME,MAX_BURST_TIME,MAX_NICE_VALUE):
    return random.randint(1, N * N),
    random.randint(0, MAX_ARRIVAL_TIME),
    random.randint(0, MAX_BURST_TIME),
    random.randint(1, MAX_NICE_VALUE)
 

if __name__ == "__main__":
    logger = create_logger('test')
    MIN_VERSION = (3, 8)
    logging.basicConfig(level = logging.WARNING)
    QUANTUM = 4  # sysctl_sched_latency 
    MAX_ARRIVAL_TIME = 20_000
    MAX_BURST_TIME = 50_000
    MAX_NICE_VALUE = 20

    N = int(input("Enter the number of tasks: "))
    TASKS = []

    print('Enter taskId, Arrival Time, CPU Burst Time, Nice value of task:')
    print('(Input Times in milliseconds)')
    for _ in range(N):
        pid, arrivalTime, burseTime, nice = tuple(int(x) for x in input().split())
        # pid, at, bt, nice = generateRandomProcess(N,MAX_ARRIVAL_TIME,MAX_BURST_TIME,MAX_NICE_VALUE)
        
        TASKS.append(
            {
                "pid": pid,
                "arrival_time": arrivalTime,
                "burst_time": burseTime,
                "nice": nice,
                "vruntime": 0,
                "exec_time": 0,
                "waiting_time": 0,
                "turnaround_time": 0,
                "weight":weightMapper(str(nice))
            }
        )

    # Sort tasks by arrival time
    TASKS_SORTED = SortedKeyList(TASKS, key=lambda task: task["arrival_time"])

    # Schedule tasks according to CFS algorithm and print average times
    initTasks(TASKS_SORTED)
    cfsSchedule(TASKS_SORTED, QUANTUM, logger)
    displayTasks(TASKS)
    findAvgTime(TASKS)

