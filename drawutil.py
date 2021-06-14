from datetime import datetime
import re
import numpy as np 
from matplotlib import pyplot as plt 
import pandas as pd
def result_drawing():
    filename = "{:%Y-%m-%d}".format(datetime.now()) + '.log'  
    path = './logs/test/' + filename
    lines = []
    with open(path, "r") as f:
        lines = f.readlines()
    f.close()

    
    # totalX = []
    # for pointData in lines:
    #     currentline = re.split(",|\n",pointData)
    #     currentline.pop() 
    #     print('currentline:',currentline)
    #     for i in len[1:len(currentline)]: #多個array
    #         tmp
        
    #     totalX.append(currentline[0])
        # totalProcess.append([currentline[0],currentline[1],currentline[2],currentline[3]]) #x,y
    # x >>ok
    # [A[],B[],C[]]
    # 

    # print(pointADict)
    # print(pointBDict)
    # print(pointCDict)
    # x_coordinates = []
    # y_coordinates = []
    # for data in pointDict[1:]:
    #     print(round(float(data[0]),3))

    #     x_coordinates.append(round(float(data[0]),3))
    #     # y_coordinates.append(round(float(data[1]),3))
        
    # plt.plot(x_coordinates, y_coordinates)
    # plt.show()
    

if __name__ == "__main__":
    print(result_drawing())