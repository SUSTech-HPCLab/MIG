import argparse

# python getUuidAll.py --input MIG_partitions.txt --raw 1 --ch 1c.3g.40gb --pick 1

MAX_GPU_NUM = 10

profile_id = {
    "0": "1c.7g.80gb",
    "5": "1c.4g.40gb",
    "9": "1c.3g.40gb",
    "14": "1c.2g.20gb",
    "19": "1c.1g.10gb",
}

def transform_ch():
    if args.ch is None or ('.' in args.ch):
        return
    args.ch = profile_id[args.ch]

parser = argparse.ArgumentParser(description='Get uuid of desired currently available MIG GPU partition')
parser.add_argument('--input', help='path to raw output / processed output of \'nvidia-smi -L\'', type = str)
parser.add_argument('--raw', help='whether is raw output or not', type = int)
parser.add_argument('--output', help='path to output file', default = None)
parser.add_argument('--ch', help='character of MIG partition to pick', type = str, default = None)
parser.add_argument('--pick', help='whether to pick the MIG partition or not', type = int, default = None)
args = parser.parse_args()

if args.output is None:
    args.output = args.input

# GPU  0 Profile ID 19 Placements: {0,1,2,3,4,5,6}:1  MIG 1g.10gb
# GPU  0 Profile ID 20 Placements: {0,1,2,3,4,5,6}:1  MIG 1g.10gb+me
# GPU  0 Profile ID 14 Placements: {0,2,4}:2          MIG 2g.20gb 
# GPU  0 Profile ID  9 Placements: {0,4}:4            MIG 3g.40gb
# GPU  0 Profile ID  5 Placement : {0}:4              MIG 4g.40gb
# GPU  0 Profile ID  0 Placement : {0}:8              MIG 7g.80gb

def read_MIG_partitions_raw(GPU, MIG):
    info_file = open(args.input)
    lines = info_file.readlines()
    info_file.close()
    output_file = open(args.output, "w")
    cur_id = 0
    cur_mig_id = 0
    tot_gpus = 0
    for line in lines:
        # print(line)
        line = line.strip(' ')
        if (line.startswith('GPU')):
            infos = line.strip('\n').split()
            # print(infos)
            mem = infos[4][ : len(infos[4]) - 2]
            uuid = infos[7].strip(')')
            cur_id = int(infos[1][ : len(infos[1]) - 1])
            cur_mig_id = 0
            GPU[cur_id] = {
                'mem': mem,
                'uuid': uuid,
            }
            tot_gpus += 1
        elif (line.startswith('MIG')):
            infos = line.strip('\n').split()
            # print(infos)
            uuid = infos[5].strip(')')
            dev_ctr = infos[1].split('.')
            # print(dev_ctr, len(dev_ctr))
            if(len(dev_ctr) == 2):
                sm_num = dev_ctr[0][: len(dev_ctr[0]) - 1]
                # print(sm_num)
                dev_ctr.insert(0, '1' + 'c')
                # print(dev_ctr)
            core_num, sm_num, mem = dev_ctr
            core_num = int(core_num[: len(dev_ctr[0]) - 1])
            sm_num = int(sm_num[: len(dev_ctr[1]) - 1])
            mem = int(mem[: len(dev_ctr[2]) - 2])
            MIG[cur_id].append({
                'core_num': core_num,
                'sm_num': sm_num,
                'mem': mem,
                'uuid': uuid,
                'used': 0
            })
            mig_str = (str(cur_id) + " " + str(cur_mig_id) + " " + \
                str(core_num) + " " + str(sm_num) + " " + str(mem) + " ")
            mig_str += str(uuid) + " " + str(0) + "\n"
            output_file.write(mig_str)
            cur_mig_id += 1
    output_file.close()
    # for i in range(tot_gpus):
    #     print("GPU: id = ", i)
    #     print(GPU[i])
    #     print("MIGs: -----------------")
    #     for id, mig in enumerate(MIG[i]):
    #         print("==> mig id = ", id)
    #         print(mig)

def read_MIG_partitions(MIG):
    info_file = open(args.input)
    lines = info_file.readlines()
    for line in lines:
        partition_info = line.strip('\n').split(' ')
        gpu_id, mig_id, core_num, sm_num, mem, uuid, used = partition_info
        gpu_id = int(gpu_id)
        mig_id = int(mig_id)
        core_num = int(core_num)
        sm_num = int(sm_num)
        mem = int(mem)
        used = bool(used)
        MIG[gpu_id].append({
            'core_num': core_num,
            'sm_num': sm_num,
            'mem': mem,
            'uuid': uuid,
            'used': 0
        })
    info_file.close()


def get_partition(MIG, charac, pick):
    core_num, sm_num, mem = charac
    core_num = int(core_num[0 : len(core_num) - 1])
    sm_num = int(sm_num[0 : len(sm_num) - 1])
    mem = int(mem[0 : len(mem) - 2])

    for gpu in MIG:
        for partition in gpu:
            if( (not pick or partition['used'] == 0) and 
                partition['core_num'] == core_num and 
                partition['sm_num'] == sm_num and 
                partition['mem'] == mem
            ):
                if(pick):
                    partition['used'] = 1
                return partition['uuid']

def write_pick(MIG, uuid):
    out_file = open(args.output)
    for gpu_id, gpu in enumerate(MIG):
        for mig_id, mig_partition in enumerate(gpu):
            if(mig_partition['uuid'] == uuid):
                mig_partition['used'] = 1
            core_num = mig_partition['core_num']
            sm_num = mig_partition['sm_num']
            mem = mig_partition['mem']
            used = mig_partition['used']
            mig_str = str(gpu_id) + " " + str(mig_id) + " " + \
                    str(core_num) + " " + str(sm_num) + " " + str(mem) + \
                    uuid + " " + str(used) + "\n"
            out_file.write(mig_str)
    out_file.close()
    return

def main():
    transform_ch()
    GPU = {}
    MIG = [[] for _ in range(MAX_GPU_NUM)]
    if(args.raw == True):
        read_MIG_partitions_raw(GPU, MIG)
    else:
        read_MIG_partitions(MIG)
    if(args.ch is not None):
        charac = args.ch.split('.')
        uuid = get_partition(MIG, charac, args.pick)
        if(args.pick):
           write_pick(MIG, uuid)
        print(uuid)

if __name__ == "__main__":
    main()