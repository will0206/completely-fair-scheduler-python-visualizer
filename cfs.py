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
    #Init process execute time data ,use for generate image

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
    
    # logger.debug(f'{listname}')
    
    while (num := len(tasks_sorted)) > 0:
        total_weight_iter = 0
        vruntime = 0
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

        timeslice = quantum #6ms
        min_task = tasks_sorted[0] #最早抵達的那個

        t_rem = min_task["burst_time"] - min_task["exec_time"]         # Time remaining for smallest task

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



        # display_tasks(tasks_sorted)
        # logger.debug(f'Executing task {min_task["pid"]} for {time} ms\n')

        # Execute process
        # vruntime = min_vruntime + time * min_nice
        vruntime = vruntime + min_vruntime  #update vruntime
        
        min_task["exec_time"] += time
        min_task["turnaround_time"] += time
        timer += time #更新現在時間 

        # update waiting and turnaround time of all other processes
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

        
        # printlog(tasks,min_task,timer,processRuntime,logger)
        taskIndex = tasks.index(min_task) #0 1 2
        
        for i in range(0,len(processes)):
            if i != taskIndex and len(processes[i])>0:
                processes[i].append(processes[i][-1])
                xcood[i].append(timer)
            else:
                processes[taskIndex].append(processRuntime[str(min_task["pid"])])
                xcood[taskIndex].append(timer)

    drawResult(xcood,processes)    

def initTasks(tasks: List[dict]):
    for task in tasks:
        task["vruntime"] = 0
        task["exec_time"] = 0
        task["waiting_time"] = 0
        task["turnaround_time"] = 0

def drawResult(xcood,processes):
    plt.title('CFS Result')  # title of the image
    plt.xlabel('CPU time (ms)')  # x axis title
    plt.ylabel('Total burst time')  # y axis title
    
    for i in range(0,len(xcood)):
        plt.plot(xcood[i],processes[i],color=(random.randint(0,255)/255,random.randint(0,255)/255,random.randint(0,255)/255))

    legendString = []
    for i in range(0,len(xcood)):
        processString = 'Process' + str(i+1)
        legendString.append(processString)
    
    plt.legend(legendString)
        
    plt.show()

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
    MAX_ARRIVAL_TIME = 20_000
    MAX_BURST_TIME = 50_000
    MAX_NICE_VALUE = 20
    QUANTUM = int(input("Enter the TimeSlice value: "))
    N = int(input("Enter the number of tasks: "))
    TASKS = []

    print('Enter taskId, Arrival Time, CPU Burst Time, Nice value of task:')
    print('(Input Times in milliseconds)')
    for _ in range(N):
        pid, arrivalTime, burseTime, nice = tuple(int(x) for x in input().split())
        # pid, at, bt, nice = generateRandomProcess(N,MAX_ARRIVAL_TIME,MAX_BURST_TIME,MAX_NICE_VALUE) #random generate process data
        
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


    TASKS_SORTED = SortedKeyList(TASKS, key=lambda task: task["arrival_time"])    # Sort tasks by arrival time

    initTasks(TASKS_SORTED)
    cfsSchedule(TASKS_SORTED, QUANTUM, logger)
