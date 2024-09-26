import sys
sys.path.append('/home/zbw/MIG/MIG_Schedule')
import queue
import util.util
import re
import glob

from itertools import permutations
from itertools import combinations
from schedule.scheduler.miso_scheduler import online_job, offline_job
from jobs.profile.standardized_throughput import get_job_list


dir = '/home/zbw/MIG/MIG_Schedule/jobs/profile/result/'
qos_list = {}
throught_list = {}

file_list = glob.glob(dir + '2_*_online.txt')
for file_name in file_list:
    with open(file_name, 'r') as f:
        file_name = file_name.replace("/home/zbw/MIG/MIG_Schedule/jobs/profile/result/", "")
   
        pattern = r'2_(.*?)_online\.txt'
        match = re.match(pattern, file_name)
        extracted_text = ''
        if match:
            extracted_text = match.group(1)
        
        qos_list[extracted_text] = []
        num = 0
        for line in f:
            qos_list[extracted_text].append([])
            line = line.strip()
            qos_list[extracted_text][num].append(line.split(" ")[0])
            qos_list[extracted_text][num].append(line.split(" ")[1])
            qos_list[extracted_text][num].append(line.split(" ")[2])
            qos_list[extracted_text][num].append(line.split(" ")[3])
            qos_list[extracted_text][num].append(line.split(" ")[4])
            qos_list[extracted_text][num].append(line.split(" ")[5])
            num = num + 1
    f.close()

file_list = glob.glob(dir + '2_*.txt')
for file_name in file_list:
    with open(file_name, 'r') as f:
        file_name = file_name.replace("/home/zbw/MIG/MIG_Schedule/jobs/profile/result/", "")
       
        pattern = r'2_(?!.*_online\.txt)(.*?)\.txt'
        match = re.match(pattern, file_name)
        extracted_text = ''
        if match:
            extracted_text = match.group(1)
        else:
            f.close()
            continue
    
        throught_list[extracted_text] = []
        num = 0
        for line in f:
            throught_list[extracted_text].append([])
            line = line.strip()
            throught_list[extracted_text][num].append(line.split(" ")[0])
            throught_list[extracted_text][num].append(line.split(" ")[1])
            throught_list[extracted_text][num].append(line.split(" ")[2])
            throught_list[extracted_text][num].append(line.split(" ")[3])
            throught_list[extracted_text][num].append(line.split(" ")[4])
            throught_list[extracted_text][num].append(line.split(" ")[5])
            num = num + 1
    f.close()


path = '/home/zbw/MIG/MIG_Schedule/jobs/profile/single_standardlized'
job_list = []

with open(path, 'r') as f:
    for line in f:
        line = line.strip()
        lines = line.split(" ")
        job_list.append(lines)
f.close()


online_job_list = get_job_list()


config_map = {7:"1c-7g-80gb", 4:"1c-4g-40gb", 3:"1c-3g-40gb", 2:"1c-2g-20gb", 1:"1c-1g-10gb"}

reverser_map = {"1c-7g-80gb" : 7, "1c-4g-40gb": 4, "1c-3g-40gb":3, "1c-2g-20gb":2, "1c-1g-10gb":1, "baseline":100}

class I_sheduler_with_over_resource:
    def __init__(self, GPU_list = [[]], max_job_per_GPU=7, cluster_algorithm='number_of_job'):
        self.GPU_list = GPU_list
        self.config_list = []
        self.max_job_per_GPU = max_job_per_GPU
        self.online_job_queue = queue.Queue()
        self.offline_job_queue = queue.Queue()
        self.throughput = []
        self.cluster_algorithm = cluster_algorithm

        for i in range(0, len(GPU_list)):
            self.config_list.append([])
            self.throughput.append(0)
       

       
    def I_cluster(self, new_job):
        index,min = self.get_index_list(self.GPU_list)
        if min + 1 <= self.max_job_per_GPU:
            jobs = []
            for i in self.GPU_list[index]:
                for j in i:
                    jobs.append(j)
            jobs.append(new_job)
           
            if(not self.partition_optimizer(jobs, index)):

                if isinstance(new_job, online_job):
                    self.online_job_queue.put(new_job)
                else:
                    self.offline_job_queue.put(new_job)
                return False
            elif isinstance(new_job, offline_job):
                throught_put = self.partition_optimizer(jobs, index)
                if throught_put < self.throughput[index]:
                 
                    jobs.remove(new_job)
                  
                    self.partition_optimizer(jobs, index)
                   
                    self.offline_job_queue.put(new_job)
                    return False
                else:
                 
                    self.throughput[index] = throught_put
            return True
        
        else:
            if isinstance(new_job, online_job):
                self.online_job_queue.put(new_job)
            else:
                self.offline_job_queue.put(new_job)
            return False
            
               
            

    def get_index_list(self, GPU_list):
        if self.cluster_algorithm == 'number_of_job':
            min_num = 9999
            index = 0
            for i in GPU_list:
                num = 0 
                for j in i:
                    for z in j:
                        num = num + 1
            
                if num < min_num:
                    min_num = num 
                    index = GPU_list.index(i)
            return index,min_num
        
        if self.cluster_algorithm == 'number_of_job_with_resource':
            num_list = []
            for i in range(0, len(self.GPU_list)):
                num = 0
                for j in self.GPU_list[i]:
                    for z in j :
                        num = num + 1
                num_list.append(num)

            min_value = min(num_list)

            GPUs = []
            for i in range(0, len(num_list)):
                if min_value == num_list[i]:
                    GPUs.append(i)

            num_resource_list = []
            for i in GPUs:     
                resource = 7
                for j in range(0, len(self.GPU_list[i])):
                    if len(self.GPU_list[i][j]) == 1:
                        if isinstance(self.GPU_list[i][j][0], online_job):
                            config_id = reverser_map.get(self.config_list[i][j])
                            resource = resource - config_id 
                        if len(self.GPU_list[i][j]) == 2:
                            config_id = reverser_map.get(self.config_list[i][j])
                            resource = resource - config_id 

                num_resource_list.append(resource)

            max_value = max(num_resource_list) 
            max_index = num_resource_list.index(max_value) 
            max_index = GPUs[max_index]
     
            min_num = 0
            for i in self.GPU_list[max_index]:
                for j in i:
                    min_num = min_num + 1
        
            return max_index, min_num
            


        if self.cluster_algorithm == 'number_of_resource':
            resource_list = []
         

            for i in range(0, len(self.GPU_list)):
                resource = 7
                for j in range(0, len(self.GPU_list[i])):
                    if len(self.GPU_list[i][j]) == 1:
                        if isinstance(self.GPU_list[i][j][0], online_job):
                            config_id = reverser_map.get(self.config_list[i][j])
                            resource = resource - config_id 
                    if len(self.GPU_list[i][j]) == 2:
                        config_id = reverser_map.get(self.config_list[i][j])
                        resource = resource - config_id 
                resource_list.append(resource)
            
            max_value = max(resource_list)
            max_index = resource_list.index(max_value) 
     
            min_num = 0
            for i in self.GPU_list[max_index]:
                for j in i:
                    min_num = min_num + 1
            return max_index, min_num
        
        if self.cluster_algorithm == 'number_of_resource_with_job':
            resource_list = []
       
            for i in range(0, len(self.GPU_list)):
                resource = 7
                for j in range(0, len(self.GPU_list[i])):
                    if len(self.GPU_list[i][j]) == 1:
                        if isinstance(self.GPU_list[i][j][0], online_job):
                            config_id = reverser_map.get(self.config_list[i][j])
                            resource = resource - config_id 
                    if len(self.GPU_list[i][j]) == 2:
                        config_id = reverser_map.get(self.config_list[i][j])
                        resource = resource - config_id 
                resource_list.append(resource)
            
            max_value = max(resource_list)

            GPUs = []
            for i in range(0, len(resource_list)):
                if max_value == resource_list[i]:
                    GPUs.append(i)
            
            num_job_list = []
            for i in GPUs:
                num = 0
                for j in self.GPU_list[i]:
                    for z in j:
                        num = num+1
                num_job_list.append(num)

            min_value = min(num_job_list) 
            min_index = num_job_list.index(min_value) 
            min_index = GPUs[min_index]
     
            min_num = 0
            for i in self.GPU_list[min_index]:
                for j in i:
                    min_num = min_num + 1
         
        
            return min_index, min_num
    
    


    def partition_optimizer(self, jobs, GPU_index):
        online_jobs = []
        offline_jobs = []
        for i in jobs:
            if isinstance(i, online_job):
                online_jobs.append(i)
            else:
                offline_jobs.append(i)
        online_config = []
        for i in online_jobs:
            config_id = self.best_fit(i)
            online_config.append(config_id)
        
        throught = self.throughput[GPU_index]

        configs = util.util.get_MIG_config()
        return self.partition_optimizer_with_online_config(jobs, GPU_index, online_config) 
       

    
    def partition_optimizer_with_online_config(self, jobs, GPU_index, online_config):
        online_jobs = []
        offline_jobs = []
        configs = util.util.get_MIG_config()
        for i in jobs:
            if isinstance(i, online_job):
                online_jobs.append(i)
            else:
                offline_jobs.append(i)
       
        online_config = online_config

        # for i in online_jobs:
        #     config_id = self.best_fit(i)

        #     online_config.append(config_id)

        concurrency_jobs = []
        for i in range(0, len(online_jobs)):
            if self.check_percentage(online_jobs[i], online_config[i]) <= 0.7:
                concurrency_jobs.append(online_jobs[i])
        
        configs = util.util.get_MIG_config()
        valid_config = []
       
        for i in configs:
            valid = True
            if len(i) >= len(online_jobs) + len(offline_jobs) - len(concurrency_jobs):
                tmp = i.copy()
                for j in online_config:
                    if j not in tmp:
                        valid = False
                        break
                    else:
                        tmp.remove(j)
                if valid:
                    valid_config.append(i.copy())
        
        if len(valid_config) == 0:
            return False
        

        config_list = []
        for i in online_jobs:
            config_list.append(config_map.get(online_config[online_jobs.index(i)]))

        for i in online_config:
           for j in valid_config:
               j.remove(i)
        
        if len(offline_jobs) == 0:
            self.GPU_list[GPU_index]  = []
            self.config_list[GPU_index] = []

            for i in range(0, len(online_jobs)):
                self.GPU_list[GPU_index].append([online_jobs[i]])
                self.config_list[GPU_index].append(config_list[i])
            return 0.0000001

        best_obj = 0
        best_config = {}
        best_concurrency  = {}

        for i in valid_config:
            
            for j in range(0, len(concurrency_jobs)+1):
                if j != 0:
                    all_combinations = list(combinations(concurrency_jobs, j))
                    if j > len(offline_jobs):
                        continue
                    for comb in all_combinations:
                        all_permutations = list(permutations(offline_jobs, j))
                        for perm in all_permutations:
                            flag_valid = True
                            tmp = offline_jobs.copy()
                       
                            throught = 0
                            concurrency = {}
                            for z in  range(0, j):
                                
                                index = online_jobs.index(comb[z])
                                if self.Calculated_throughput_double(comb[z], perm[z], config_map.get(online_config[index])):
                                    throught = throught +  self.Calculated_throughput_double(comb[z], perm[z], config_map.get(online_config[index]))

                                    tmp.remove(perm[z])
                                    concurrency[comb[z]] = perm[z]
                                else:
                                    flag_valid = False
                                    break
                           
                            if flag_valid:
                             

                                all_combinations2 = list(permutations(i, len(tmp)))
                                tmp_config = []
                                tmp_throught = 0
                                for combo2 in all_combinations2:
                                    config = []
                                   
                                    for k in combo2:
                                        config.append(config_map.get(k))
                                 
                                    middle_throught =self.Calculated_throughput(config, tmp)
                                    tmp_dic = {}
                                    for k in range(0, len(tmp)):
                                        tmp_dic[tmp[k]] = config[k]
                                    if middle_throught > tmp_throught:
                                        tmp_throught = middle_throught
                                        tmp_config = tmp_dic

                                if throught + tmp_throught > best_obj:
                                    if len(tmp) == 0 and len(config) == 0:
                                        tmp_config = {}
                                    best_config = tmp_config
                                    best_obj = throught + tmp_throught
                                    best_concurrency = concurrency
                            else:
                                continue
                else:
                    concurrency = {}
                    throught = 0
                    tmp = offline_jobs.copy()
                    if len(tmp) > len(i):
                        continue
                    all_combinations2 = list(permutations(i, len(tmp)))
                    for combo2 in all_combinations2:
                        config = []
                        for k in combo2:
                            config.append(config_map.get(k))
                        throught = self.Calculated_throughput(config, tmp) 
                        tmp_dic = {}

                        for k in range(0, len(tmp)):
                            tmp_dic[tmp[k]] = config[k]

                        config = tmp_dic
                        if throught > best_obj:
                            best_config = config
                            best_obj = throught
                            best_concurrency = concurrency

        if best_obj == 0 :
            return False

        self.GPU_list[GPU_index]  = []
        self.config_list[GPU_index] = []

        for i in range(0, len(online_jobs)):
            self.GPU_list[GPU_index].append([online_jobs[i]])
            self.config_list[GPU_index].append(config_list[i])
  
        for i in best_concurrency.keys():
            offline = best_concurrency.get(i)
 
            self.GPU_list[GPU_index][online_jobs.index(i)].append(offline)

        for i in best_config.keys():
           
            self.GPU_list[GPU_index].append([i])
            self.config_list[GPU_index].append(best_config.get(i))

        return best_obj


   
    def Calculated_throughput(self, config_list, jobs):
        throughput = 0
        global job_list
        for i in job_list:
            
            for j in range(0, len(jobs)):

                if jobs[j].model_name == i[0] and int(jobs[j].batch_Size) == int(i[1]) and config_list[j] == i[2]:
                    throughput = throughput + float(i[3])
    

        return throughput
    
    def best_fit(self, online_job):
     
        global online_job_list
        MIG_partition_list = []
        for i in online_job_list:
            if i.model_name == online_job.model_name and int(i.batch_Size)== int(online_job.batch_Size) and float(i.tail) < online_job.qos:
                MIG_partition_list.append(i.config)


        min = 100
        for i in range(0, len(MIG_partition_list)):
            GI = reverser_map[MIG_partition_list[i]]
            if GI:
                if GI <= min:
                    min = GI

        return min
    

    def state_change(self, GPU_index, job):
        for i in self.GPU_list[GPU_index]:
            if job in i:
                index = i.index(job)
             
                if len(i) >= 2:
                    i.remove(job)

                else:
                    self.GPU_list[GPU_index].remove(i)
                    del self.config_list[GPU_index][index] 
                 
                break
        jobs = []
        for i in self.GPU_list[GPU_index]:
            for j in i:
                jobs.append(j)

        self.throughput[GPU_index] = self.partition_optimizer(jobs, GPU_index)



        flag = True
        
        if not self.online_job_queue.empty():
            online_job = self.online_job_queue.get()
            result = self.I_cluster(online_job)
            if result:
                flag = False
                
        
        if flag:
            if not self.offline_job_queue.empty():
                offline_job = self.offline_job_queue.get()
                result = self.I_cluster(offline_job)
               






                
              
                
                       



    def check_percentage(self, online_job, config_id):
        global online_job_list
   
        config = config_map.get(config_id)
   
        for i in online_job_list:
            if i.model_name == online_job.model_name and int(i.batch_Size)== int(online_job.batch_Size) and i.config == config:
                return float(i.tail)/float(online_job.qos)
        
            
    def Calculated_throughput_double(self, online_job: online_job, offline_job: offline_job, config):
        global qos_list, throught_list
       
        for i in qos_list[config]:
          
            if i[0] == online_job.model_name and int(i[1]) == int(online_job.batch_Size) and i[3] == offline_job.model_name and \
                int(i[4]) == int(offline_job.batch_Size):
           
               
                if i[2] == 'error' or float(i[2]) >  float(online_job.qos) or i[5] == 'error':
                    return False
                
          
                
            if i[0] == offline_job.model_name and int(i[1]) == int(offline_job.batch_Size) and i[3] == online_job.model_name and \
                int(i[4]) == int(online_job.batch_Size):
          
                if i[5] == 'error' or float(i[5]) > float(online_job.qos) or i[2] == 'error':
                    return False

      
       

        base = 0 
        for i in online_job_list:
         
            if i.model_name == offline_job.model_name and int(i.batch_Size) == int(offline_job.batch_Size) and i.config == '1c-7g-80gb':
                base = float(i.average_time)
                break
     
        for i in throught_list[config]:

            if i[0] == online_job.model_name and int(i[1]) == int(online_job.batch_Size) and i[3] == offline_job.model_name and \
                int(i[4]) == int(offline_job.batch_Size):
         
          
                return base/float(i[5])
                
            if i[0] == offline_job.model_name and int(i[1]) == int(offline_job.batch_Size) and i[3] == online_job.model_name and \
                int(i[4]) == int(online_job.batch_Size):
          
                
                return base/float(i[2])
        
            


        return False











        
