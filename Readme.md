
# CFS Scheduler 
Fork from [SanchithHegde/completely-fair-scheduler](https://github.com/SanchithHegde/completely-fair-scheduler).
## 程式說明:

1. 此程式用於demo CFS Scheduler in Linux內的對應流程，使用者輸入對應的Time slice , numbers of tasks , task data(id, arrival time, burst time )

## 操作說明:
1. 於專案資料夾當層輸入python cfs.py
2. 輸入對應的Time slice , numbers of tasks , task data(id, arrival time, burst time )
3. 程式執行後會以圖片顯示排程的執行運算結果


## Sample Input ##

  1. TestCase 1 : 4 tasks with same arrived time, nice value and the same burst time.

    6
    4
    1 0 100 0
    2 0 100 0
    3 0 100 0
    4 0 100 0

  2. TestCase 2 : 3 tasks with max and mix nice value.

    6
    3
    1 0 1000 19
    2 0 1000 0
    3 0 1000 -20


  3. TestCase 3 : 3 tasks with one task arrived earlier then others.

    6
    3
    1 1000 3000 0
    2 2000 4000 -2
    3 2000 3000 2
    
Result

![image](https://user-images.githubusercontent.com/25097700/122734935-206d2400-d2b1-11eb-8de8-367e63d4b4d6.png)

