from MLP_train import MLP_train
from resnet_train import resnet_train
from vgg_train import vgg_train
from alexnet_train import alxnet_train
import subprocess
import argparse
import time
task_table = {
    'mlp' : MLP_train,
    'resnet':  resnet_train,
    'vgg19': vgg_train,
    'alexnet': alxnet_train,
}
def run_command(command):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,  
            text=True, 
            shell=True  
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(e)


parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
parser.add_argument("--profile", type=bool, default=False)
parser.add_argument("--config", type=str, required=False)
args = parser.parse_args()

task = args.model
config = args.config
profile = args.profile
start = time.time()
if task == 'unet':
    command_to_run = "cd /home/zbw/MIG/MIG_Schedule/jobs/offline/Unet && conda run -n Abacus python train.py --amp"
    run_command(command_to_run)
else:
    entry = task_table[task]
    entry()

end = time.time()
if profile:
    with open('/home/zbw/MIG/MIG_Schedule/jobs/profile/single_offline', "a+") as f:
        result = config + ' ' + task + ' ' + str((end - start)/60) +  '\n'
        f.write(result)


