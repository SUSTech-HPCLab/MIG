import glob
import csv
class job:
    def __init__(self, model_name, config, batch_Size, average_time, tail):
        self.model_name = model_name
        self.config = config
        self.batch_Size = batch_Size
        self.average_time = average_time
        self.tail = tail
    def __str__(self):
        return f"Model Name: {self.model_name} Config: {self.config} Batch Size: {self.batch_Size} Average Time: {self.average_time} Tail: {self.tail}"


def get_job_list():
    job_list = []
    dir = '/home/zbw/MIG/MIG_Schedule/jobs/profile/result/'
    file_list = glob.glob(dir + '*_MIG.txt')
    for file_name in file_list:
        with open(file_name, 'r') as f:
            file_name = file_name.replace("/home/zbw/MIG/MIG_Schedule/jobs/profile/result/", "")
            model_name = file_name.replace("_MIG.txt", "")
            input = []
            count = 0
            for line in f:
                if count == 0:
                    input.append(line.split(':')[1].strip())
                if count == 1:
                    input.append(int(line.split(':')[1].strip()))
                if count == 2 or count == 3:
                    input.append(float(line.split(':')[1].strip()) * 1000)
                count = count + 1
                if count >= 4:
                    # if input[0] != 'baseline':
                    #     count = 0
                    #     input = []
                    #     continue
                    tep_job = job(model_name=model_name, config=input[0], batch_Size=input[1], average_time=input[2], tail=input[3])
                    job_list.append(tep_job)
                    count = 0
                    input = []
        f.close()
    return job_list


def standardlized_single():
    dir = '/home/zbw/MIG/MIG_Schedule/jobs/profile/'

    job_list = get_job_list()
    batch_size = []
    model_name = []
    config = []

    for i in job_list:
        if i.model_name not in model_name:
            model_name.append(i.model_name)

        if i.batch_Size not in batch_size:
            batch_size.append(i.batch_Size)
        
        if i.config not in config:
            config.append(i.config)

    base_dic = {}
    for i in model_name:
        base_dic[i] = {}

    for i in job_list:
        if i.config == 'baseline':
            base_dic[i.model_name][i.batch_Size] = i.average_time


    throught_dic = {}
    for i in model_name:
        throught_dic[i] = {}
        for j in batch_size:
            throught_dic[i][j] = {}

    for i in job_list:
        throught = base_dic[i.model_name][i.batch_Size] / i.average_time
        throught_dic[i.model_name][i.batch_Size][i.config] = throught
    
    return base_dic
    with open(dir+"single_standardlized", "a+") as file:
        for i in model_name:
            for j in batch_size:
                for z in config:
                    input = i + " " + str(j) + " " + z + " " +  str(throught_dic[i][j][z]) + "\n"
                    file.write(input)
    file.close()


def standardlized_double():
    dir = '/home/zbw/MIG/MIG_Schedule/jobs/profile/'
    base_dic =  standardlized_single()

    run_list = []
    with open('/home/zbw/MIG/MIG_Schedule/jobs/profile/result/2.txt', 'r') as f:
        for line in f:
            line = line.strip()
            line_list = line.split(" ")
            run_list.append(line_list)

    f.close()



    print(base_dic)

    with open(dir+"double_base_standardlized", "a+") as file:
        # input = i + " " + str(j) + " " + z + " " +  str(throught_dic[i][j][z]) + "\n"
        
        for i in run_list:
            model1 = i[0]
            model2 = i[3]
            batch1 = i[1]
            batch2 = i[4]
            throught1 =  base_dic[model1][int(batch1)] / float(i[2])
            throught2 =  base_dic[model2][int(batch2)] / float(i[5])
            input = model1 + " " + str(batch1) + " " + str(throught1) + " " + model2 + " " +str(batch2) + " " + str(throught2) + "\n" 
            file.write(input)
    file.close()

if __name__ == "__main__":
    standardlized_double()