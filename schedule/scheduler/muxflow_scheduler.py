
import sys
sys.path.append('/home/zbw/MIG/MIG_Schedule')

import numpy as np
import queue
from schedule.scheduler.miso_scheduler import online_job, offline_job
from schedule.KM import KM
from jobs.profile.standardized_throughput import job
path = '/home/zbw/MIG/MIG_Schedule/jobs/profile/double_base_standardlized'
job_list =[]
with open(path, 'r') as f:
    for line in f:
        line = line.strip()
        lines = line.split(" ")
        job_list.append(lines)
f.close()

class muxflow_sheduler:
    def __init__(self, GPU_list=[]):
        self.GPU_list = GPU_list
        self.online_job_queue = queue.Queue()
        self.offline_job_queue = queue.Queue()
    

    def binomial_matching(self, Net):
        net = np.array(Net)
        km = KM()
        max_ = km.compute(net.copy())
        result = []
        print(max_)
        for i in max_:
            result.append(i[1])
        return result

    def join_job(self, job):
        pass

    def muxflow(self, online_jobs, offline_jobs):
        
        online_job_GPU = [0] * len(online_jobs)
        num = 0 
        for i in online_jobs:
            for j in range(0, len(self.GPU_list)):
                if len(self.GPU_list[j]) == 0:
                    self.GPU_list[j].append(i)
                    online_job_GPU[num] = j
                    break
            num = num + 1
        net = []
        for i in online_jobs:
            throught_matrix = []
            for j in offline_jobs:
                throught_matrix.append(int(self.predict(i,j) * 10000))
            net.append(throught_matrix.copy())
        result = self.binomial_matching(net)
        for i in range(0, len(result)):
            if result[i] != -1:
                self.GPU_list[online_job_GPU[i]].append(offline_jobs[result[i]])

    def predict(self, online, offline):

        global job_list
        for i in job_list:
            if (online.model_name == i[0] and int(online.batch_Size) == int(i[1])  and offline.model_name == i[3] and int(offline.batch_Size) == int(i[4])) or \
            (offline.model_name == i[0] and int(offline.batch_Size) == int(i[1])  and online.model_name == i[3] and int(online.batch_Size) == int(i[4])):
                return float(i[5]) 
            

# test1 = online_job('alexnet', '16', 80)
# test5 = online_job('resnet50', '16', 80)
# test6 = online_job('resnet50', '16', 80)

# test2 = offline_job("bert", '32', 100)
# test3 = offline_job("bert", '32', 100)
# test4 = offline_job("mobilenet_v2", '32', 100)
# test = miso_sheduler(GPU_list=[[],[]])

# online = []
# online.append(test1)
# # online.append(test5)
# # online.append(test6)
# offline = []
# offline.append(test2)
# offline.append(test3)
# test.muxflow(online_jobs=online, offline_jobs=offline)




    