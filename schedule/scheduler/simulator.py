
import sys
import re
import glob
import random
import copy
sys.path.append('/home/zbw/MIG/MIG_Schedule')
from schedule.scheduler.miso_scheduler import online_job, offline_job, miso_sheduler
from schedule.scheduler.scheduler_with_over_resource import I_sheduler_with_over_resource
from schedule.scheduler.scheduler import I_sheduler
from schedule.scheduler.muxflow_scheduler import muxflow_sheduler
from jobs.profile.standardized_throughput import get_job_list



random.seed(15)

job_list = get_job_list()

dir = '/home/zbw/MIG/MIG_Schedule/jobs/profile/result/'
throught_list = {}
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



class simulator:
    def __init__(self, GPU_num, algorithm, online_jobs, offline_jobs, num=4, cluster_algorithm='number_of_job'):
        self.GPU_num = GPU_num
        self.algorithm = algorithm
        self.online_jobs = online_jobs
        self.offline_jobs = offline_jobs
        self.num = num
        self.queue_time = []
        self.JCT = []
        self.config_num = 0
        self.cluster_algorithm = cluster_algorithm
        self.simulate()

    def simulate(self):
        if self.algorithm == 'miso':
            checkpoint_time = 0
            GPU_list = []
            for i in range(0, self.GPU_num):
                GPU_list.append([])

            miso = miso_sheduler(GPU_list= GPU_list, cluster_algorithm=self.cluster_algorithm)
            for i in self.online_jobs:
                miso.miso_cluster(i)
        
            for i in self.offline_jobs:
                if  miso.miso_cluster(i):
                    i.start_time = 0 
          
            for i in range(0, len(miso.GPU_list)):
                jobs = miso.GPU_list[i]
                configs = miso.config_list[i]


                for j in range(0, len(jobs)):
                    if isinstance(jobs[j], online_job):
                        continue
                        
                    if isinstance(jobs[j], offline_job):
                        self.caculate_completion_time(jobs[j], configs[j])
            
       
            num = 0
            job_list = []
            while True:
               
                num = num + 1
                for i in range(0, len(miso.GPU_list)):
                    remove_jobs = []
                    for j in range(0, len(miso.GPU_list[i])):
                        if isinstance(miso.GPU_list[i][j], offline_job):
                           
                           miso.GPU_list[i][j].progress = miso.GPU_list[i][j].progress + miso.GPU_list[i][j].speed
                           if miso.GPU_list[i][j].progress >= miso.GPU_list[i][j].epoch:
                               remove_jobs.append(miso.GPU_list[i][j])

                    if len(remove_jobs) != 0:
                        for z in remove_jobs:
                            z.end_time = num
                            job_list.append(z)
                            miso.state_change(i,z)

                        for j in range(0, len(miso.GPU_list)):
                            for z in range(0, len(miso.GPU_list[j])):
                                if isinstance(miso.GPU_list[j][z], online_job):
                                    continue
                                if isinstance(miso.GPU_list[j][z], offline_job):
                                    if  miso.GPU_list[j][z].start_time == -1:
                                        miso.GPU_list[j][z].start_time = num
                                    self.caculate_completion_time(miso.GPU_list[j][z], miso.config_list[j][z])
                # print(len(job_list))
                if len(job_list) == self.num:
                    # for i in job_list:
                    #     print(i)
                    break
            self.caculate_system_metrics(jobs=job_list)

        if self.algorithm == 'me':
            GPU_list = []
            for i in range(0, self.GPU_num):
                GPU_list.append([])
            
            scheduler = I_sheduler(GPU_list= GPU_list, cluster_algorithm=self.cluster_algorithm)
            for i in self.online_jobs:
                scheduler.I_cluster(i)

            for j in self.offline_jobs:
                if scheduler.I_cluster(j):
                    j.start_time = 0 
          
            
            for i in range(0, len(scheduler.GPU_list)):
                configs = scheduler.config_list[i]

                for j in range(0, len(scheduler.GPU_list[i])):
                    if len(scheduler.GPU_list[i][j]) == 1:
                        if isinstance(scheduler.GPU_list[i][j][0], online_job):
                            continue
                        if isinstance(scheduler.GPU_list[i][j][0], offline_job):
                            self.caculate_completion_time(scheduler.GPU_list[i][j][0], configs[j])
                    
                    else:
                        if isinstance(scheduler.GPU_list[i][j][0], online_job):
                            self.caculate_completion_time_concurrency(scheduler.GPU_list[i][j][1], scheduler.GPU_list[i][j][0] ,configs[j])
                        else:
                            self.caculate_completion_time_concurrency(scheduler.GPU_list[i][j][0], scheduler.GPU_list[i][j][1] ,configs[j])
            

            num = 0
            job_list = []
          
            c = 0
            
            while True:
                num = num + 1
                 
                for i in range(0, len(scheduler.GPU_list)):
                 
                    remove_jobs = []
                    for j in range(0, len(scheduler.GPU_list[i])):
                        if len(scheduler.GPU_list[i][j]) == 1:
                            if isinstance(scheduler.GPU_list[i][j][0], offline_job):
                                scheduler.GPU_list[i][j][0].progress = scheduler.GPU_list[i][j][0].progress + scheduler.GPU_list[i][j][0].speed
                                if scheduler.GPU_list[i][j][0].progress >= scheduler.GPU_list[i][j][0].epoch:
                                    remove_jobs.append(scheduler.GPU_list[i][j][0])
                        else:
                            if isinstance(scheduler.GPU_list[i][j][0], offline_job):
                                scheduler.GPU_list[i][j][0].progress = scheduler.GPU_list[i][j][0].progress + scheduler.GPU_list[i][j][0].speed
                                if scheduler.GPU_list[i][j][0].progress >= scheduler.GPU_list[i][j][0].epoch:
                                    remove_jobs.append(scheduler.GPU_list[i][j][0])
                                    c =  c + 1
                            else:
                                scheduler.GPU_list[i][j][1].progress = scheduler.GPU_list[i][j][1].progress + scheduler.GPU_list[i][j][1].speed
                                if scheduler.GPU_list[i][j][1].progress >= scheduler.GPU_list[i][j][1].epoch:
                                    remove_jobs.append(scheduler.GPU_list[i][j][1])
                                    c =  c + 1

                    if len(remove_jobs) != 0:
                        for z in remove_jobs:
                           
                            z.end_time = num
                            job_list.append(z)
                         
                            scheduler.state_change(i,z)
                     
                       
                        for j in range(0, len(scheduler.GPU_list)):
                        
                            for z in range(0, len(scheduler.GPU_list[j])):
                                if len(scheduler.GPU_list[j][z]) == 1:
                                    if isinstance(scheduler.GPU_list[j][z][0], online_job):
                                        continue
                                    if isinstance(scheduler.GPU_list[j][z][0], offline_job):
                                        if  scheduler.GPU_list[j][z][0].start_time == -1:
                                            scheduler.GPU_list[j][z][0].start_time = num
                    
                                        self.caculate_completion_time(scheduler.GPU_list[j][z][0], scheduler.config_list[j][z])
                    
                                else:
                                    if isinstance(scheduler.GPU_list[j][z][0], online_job):
                                        if  scheduler.GPU_list[j][z][1].start_time == -1:
                                            scheduler.GPU_list[j][z][1].start_time = num
                                        self.caculate_completion_time_concurrency(scheduler.GPU_list[j][z][1], scheduler.GPU_list[j][z][0], scheduler.config_list[j][z])
                                    else:
                                        if  scheduler.GPU_list[j][z][0].start_time == -1:
                                            scheduler.GPU_list[j][z][0].start_time = num
                                        self.caculate_completion_time_concurrency(scheduler.GPU_list[j][z][0], scheduler.GPU_list[j][z][1], scheduler.config_list[j][z])
       
                if len(job_list) == self.num:
                    # for i in job_list:
                    #     print(i)
                    print(c)
                    break
                
        if self.algorithm == 'me_with_over_resource':
            GPU_list = []
            for i in range(0, self.GPU_num):
                GPU_list.append([])
            
            scheduler = I_sheduler_with_over_resource(GPU_list= GPU_list, cluster_algorithm=self.cluster_algorithm)
            for i in self.online_jobs:
                scheduler.I_cluster(i)

            for j in self.offline_jobs:
                if scheduler.I_cluster(j):
                    j.start_time = 0 
          
            
            for i in range(0, len(scheduler.GPU_list)):
                configs = scheduler.config_list[i]

                for j in range(0, len(scheduler.GPU_list[i])):
                    if len(scheduler.GPU_list[i][j]) == 1:
                        if isinstance(scheduler.GPU_list[i][j][0], online_job):
                            continue
                        if isinstance(scheduler.GPU_list[i][j][0], offline_job):
                            self.caculate_completion_time(scheduler.GPU_list[i][j][0], configs[j])
                    
                    else:
                        if isinstance(scheduler.GPU_list[i][j][0], online_job):
                            self.caculate_completion_time_concurrency(scheduler.GPU_list[i][j][1], scheduler.GPU_list[i][j][0] ,configs[j])
                        else:
                            self.caculate_completion_time_concurrency(scheduler.GPU_list[i][j][0], scheduler.GPU_list[i][j][1] ,configs[j])
            

            num = 0
            job_list = []
          
            c = 0
            
            while True:
                num = num + 1
                 
                for i in range(0, len(scheduler.GPU_list)):
                 
                    remove_jobs = []
                    for j in range(0, len(scheduler.GPU_list[i])):
                        if len(scheduler.GPU_list[i][j]) == 1:
                            if isinstance(scheduler.GPU_list[i][j][0], offline_job):
                                scheduler.GPU_list[i][j][0].progress = scheduler.GPU_list[i][j][0].progress + scheduler.GPU_list[i][j][0].speed
                                if scheduler.GPU_list[i][j][0].progress >= scheduler.GPU_list[i][j][0].epoch:
                                    remove_jobs.append(scheduler.GPU_list[i][j][0])
                        else:
                            if isinstance(scheduler.GPU_list[i][j][0], offline_job):
                                scheduler.GPU_list[i][j][0].progress = scheduler.GPU_list[i][j][0].progress + scheduler.GPU_list[i][j][0].speed
                                if scheduler.GPU_list[i][j][0].progress >= scheduler.GPU_list[i][j][0].epoch:
                                    remove_jobs.append(scheduler.GPU_list[i][j][0])
                                    c =  c + 1
                            else:
                                scheduler.GPU_list[i][j][1].progress = scheduler.GPU_list[i][j][1].progress + scheduler.GPU_list[i][j][1].speed
                                if scheduler.GPU_list[i][j][1].progress >= scheduler.GPU_list[i][j][1].epoch:
                                    remove_jobs.append(scheduler.GPU_list[i][j][1])
                                    c =  c + 1

                    if len(remove_jobs) != 0:
                        for z in remove_jobs:
                           
                            z.end_time = num
                            job_list.append(z)
                         
                            scheduler.state_change(i,z)
                     
                       
                        for j in range(0, len(scheduler.GPU_list)):
                        
                            for z in range(0, len(scheduler.GPU_list[j])):
                                if len(scheduler.GPU_list[j][z]) == 1:
                                    if isinstance(scheduler.GPU_list[j][z][0], online_job):
                                        continue
                                    if isinstance(scheduler.GPU_list[j][z][0], offline_job):
                                        if  scheduler.GPU_list[j][z][0].start_time == -1:
                                            scheduler.GPU_list[j][z][0].start_time = num
                    
                                        self.caculate_completion_time(scheduler.GPU_list[j][z][0], scheduler.config_list[j][z])
                    
                                else:
                                    if isinstance(scheduler.GPU_list[j][z][0], online_job):
                                        if  scheduler.GPU_list[j][z][1].start_time == -1:
                                            scheduler.GPU_list[j][z][1].start_time = num
                                        self.caculate_completion_time_concurrency(scheduler.GPU_list[j][z][1], scheduler.GPU_list[j][z][0], scheduler.config_list[j][z])
                                    else:
                                        if  scheduler.GPU_list[j][z][0].start_time == -1:
                                            scheduler.GPU_list[j][z][0].start_time = num
                                        self.caculate_completion_time_concurrency(scheduler.GPU_list[j][z][0], scheduler.GPU_list[j][z][1], scheduler.config_list[j][z])
       
                if len(job_list) == self.num:
                    # for i in job_list:
                    #     print(i)
                    print(c)
                    break
            self.caculate_system_metrics(jobs=job_list)


    def caculate_completion_time(self, offline_job, config):
        global job_list
        for i in job_list:
            if i.model_name == offline_job.model_name and str(i.batch_Size) == str(offline_job.batch_Size) and config == i.config:
                offline_job.speed = 1000/float(i.average_time)
                break
    
    def caculate_completion_time_concurrency(self, offline_job:offline_job, online_job:online_job, config):
        for i in throught_list[config]:

            if i[0] == online_job.model_name and int(i[1]) == int(online_job.batch_Size) and i[3] == offline_job.model_name and \
                int(i[4]) == int(offline_job.batch_Size):
                offline_job.speed = 1000/float(i[5])
                
            if i[0] == offline_job.model_name and int(i[1]) == int(offline_job.batch_Size) and i[3] == online_job.model_name and \
                int(i[4]) == int(online_job.batch_Size):
                offline_job.speed =  1000/float(i[2])

    def caculate_system_metrics(self, jobs):
        avarage_queue_time = 0
        JCT = 0
        makespan = 0
        num = len(jobs)
        for i in jobs:
            avarage_queue_time = avarage_queue_time + int(i.start_time) - int(i.submit_time)
            JCT = JCT + int(i.end_time) - int(i.submit_time)
            if int(i.end_time) > makespan:
                makespan = i.end_time
        

        avarage_queue_time = avarage_queue_time/num
        JCT = JCT/num

        print("avarage_queue_time : ", avarage_queue_time)
        print("JCT: ", JCT)
        print("makespan: ", makespan)






def offline_job_generator(num):
    job_list = ['alexnet', 'bert', 'deeplabv3', 'inception_v3', 'mobilenet_v2', 'resnet50', 'resnet101', 'resnet152', 'unet', 'vgg16', 'vgg19']
    base_size_list = [4,8,16,32]
    epoch_num = [100000,200000,300000,400000,500000,600000,700000,800000,900000,1000000]
    offline_job_list = []
    for i in range(0, num):
        # random_ID = random.randint(1, 1000000)
        random_model = random.choice(job_list)
        random_batch = random.choice(base_size_list)
        random_epoch = random.choice(epoch_num)
        random_epoch = random_epoch * 10
        offline_job_list.append(offline_job(random_model, random_batch, random_epoch))
    return offline_job_list

def online_job_generator(num):
    global job_list
    online_job_list = []
    job_name_list = ['alexnet', 'bert', 'deeplabv3', 'inception_v3', 'mobilenet_v2', 'resnet50', 'resnet101', 'resnet152', 'unet', 'vgg16', 'vgg19']
    base_size_list = [4,8,16,32]
    config_map = {7:"1c-7g-80gb", 4:"1c-4g-40gb", 3:"1c-3g-40gb", 2:"1c-2g-20gb", 1:"1c-1g-10gb"}
    
    test =  I_sheduler()
    for i in range(0, num):
        qos = [40,50,60,70,80,90,100,110,120,130,140,150,160,170]
       
        while True:
            random_batch = random.choice(base_size_list)
            random_model = random.choice(job_name_list)
            random_qos = random.choice(qos)

            flag = False
            online_job_item = online_job(model_name=random_model, batch_Size=random_batch, qos=random_qos)
            if test.best_fit(online_job=online_job_item) != 100:
                config_id = test.best_fit(online_job=online_job_item)
                config  = config_map.get(config_id)
                
                for j in job_list:
                    if j.model_name == online_job_item.model_name and int(j.batch_Size)== int(online_job_item.batch_Size) and j.config == config:
                        if float(j.tail)/online_job_item.qos < 0.6:
                            online_job_list.append(online_job_item)
                            flag = True
                            break
                        else:
                            break
            if flag:
                break  
                            
    return online_job_list

# for i in job_list:
#     print(i)
gpu_num = 8
offline_jobs = offline_job_generator(50)
online_jobs = online_job_generator(10)

# test = simulator(GPU_num=gpu_num, algorithm='miso', cluster_algorithm='number_of_job_with_resource', online_jobs=copy.deepcopy(online_jobs), offline_jobs=copy.deepcopy(offline_jobs), num=len(offline_jobs))






# test2 = simulator(GPU_num=gpu_num, algorithm='me', cluster_algorithm='number_of_job_with_resource', online_jobs= copy.deepcopy(online_jobs), offline_jobs=copy.deepcopy(offline_jobs), num=len(offline_jobs))

test3 = simulator(GPU_num=gpu_num, algorithm='me_with_over_resource', cluster_algorithm='number_of_job_with_resource', online_jobs= copy.deepcopy(online_jobs), offline_jobs=copy.deepcopy(offline_jobs), num=len(offline_jobs))

