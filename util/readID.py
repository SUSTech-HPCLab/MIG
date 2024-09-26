import argparse

# python getUuidAll.py --input MIG_partitions.txt --raw 1 --ch 1c.3g.40gb --pick 1

parser = argparse.ArgumentParser(description='Get uuid of desired currently available MIG GPU partition')
parser.add_argument('--input', help='path to output of \'nvidia-smi mig -cgi \'', type = str)
args = parser.parse_args()

def read_ID():
    ids = []
    with open(args.input) as file:
        lines = file.readlines()
        for line in lines:
            info = line.split()
            if(info[2] == 'GPU'):
                ids.append(info[5])
    # print("------------------ " + len(ids))
    for i, id in enumerate(ids):
        if(i != len(ids) - 1):
            #print(id + ",", end = '')
            pass 
        else:
            print(id)

def main():
    read_ID()

if __name__ == "__main__":
    main()