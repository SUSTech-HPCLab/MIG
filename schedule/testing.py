import os
import threading
import subprocess
import time
MIG_UUID = 'MIG-32522c13-1a59-5776-9d30-e0ae7b6a4874'

CUDA_MPS_PIPE_DIRECTORY = f'/tmp/{MIG_UUID}-pipe'
CUDA_MPS_LOG_DIRECTORY=f'/tmp/{MIG_UUID}-log'

def execute_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate() 

# pid = 978806

cmd = f'export CUDA_MPS_PIPE_DIRECTORY={CUDA_MPS_PIPE_DIRECTORY} && export CUDA_MPS_LOG_DIRECTORY={CUDA_MPS_LOG_DIRECTORY} && export CUDA_VISIBLE_DEVICES={MIG_UUID} && echo quit | sudo -E  nvidia-cuda-mps-control'
result = subprocess.check_output(cmd, shell=True)
result = result.decode().strip()

# cmd = f'export CUDA_MPS_PIPE_DIRECTORY={CUDA_MPS_PIPE_DIRECTORY} && export CUDA_MPS_LOG_DIRECTORY={CUDA_MPS_LOG_DIRECTORY} && export CUDA_VISIBLE_DEVICES={MIG_UUID} && sudo -E nvidia-cuda-mps-control -d && (echo start_server -uid 1002 | sudo -E nvidia-cuda-mps-control) '
# result = subprocess.check_output(cmd, shell=True)
# result = result.decode().strip()

# cmd=f'cd /home/zbw/MIG/MIG_Schedule/schedule && export CUDA_MPS_PIPE_DIRECTORY={CUDA_MPS_PIPE_DIRECTORY} && export CUDA_MPS_LOG_DIRECTORY={CUDA_MPS_LOG_DIRECTORY} && CUDA_VISIBLE_DEVICES={MIG_UUID}  python warm.py'
# result = subprocess.check_output(cmd, shell=True)
# result = result.decode().strip()


# print("1")
# cmd = f'export CUDA_MPS_PIPE_DIRECTORY={CUDA_MPS_PIPE_DIRECTORY} && export CUDA_MPS_LOG_DIRECTORY={CUDA_MPS_LOG_DIRECTORY} && export CUDA_VISIBLE_DEVICES={MIG_UUID} && (echo get_server_list | sudo -E nvidia-cuda-mps-control)'
# result = subprocess.check_output(cmd, shell=True)
# result = result.decode().strip()
# pid = result
# print("2")

# cmd = f'export CUDA_MPS_PIPE_DIRECTORY={CUDA_MPS_PIPE_DIRECTORY} && export CUDA_MPS_LOG_DIRECTORY={CUDA_MPS_LOG_DIRECTORY} && export CUDA_VISIBLE_DEVICES={MIG_UUID} && echo set_active_thread_percentage {pid} {100} | sudo -E nvidia-cuda-mps-control'
# result = subprocess.check_output(cmd, shell=True)
# result = result.decode().strip()

# print("3")
# cmd=f'cd /home/zbw/MIG/MIG_Schedule/schedule && export CUDA_MPS_PIPE_DIRECTORY={CUDA_MPS_PIPE_DIRECTORY} && export CUDA_MPS_LOG_DIRECTORY={CUDA_MPS_LOG_DIRECTORY} && CUDA_VISIBLE_DEVICES={MIG_UUID}  python test_program.py'
# result = subprocess.check_output(cmd, shell=True)
# result = result.decode().strip()
# command_thread = threading.Thread(target=execute_command, args=(cmd,))
# command_thread.start()
# cmd = f'export CUDA_MPS_PIPE_DIRECTORY={CUDA_MPS_PIPE_DIRECTORY} && export CUDA_MPS_LOG_DIRECTORY={CUDA_MPS_LOG_DIRECTORY} && export CUDA_VISIBLE_DEVICES={MIG_UUID} && echo get_active_thread_percentage {pid} | sudo -E nvidia-cuda-mps-control'
# print(cmd)
# result = subprocess.check_output(cmd, shell=True)
# result = result.decode().strip()


# cmd = f'export CUDA_MPS_PIPE_DIRECTORY={CUDA_MPS_PIPE_DIRECTORY} && export CUDA_MPS_LOG_DIRECTORY={CUDA_MPS_LOG_DIRECTORY} && export CUDA_VISIBLE_DEVICES={MIG_UUID} && echo quit | sudo -E  nvidia-cuda-mps-control'
# result = subprocess.check_output(cmd, shell=True)
# result = result.decode().strip()
# if result == '':
#     print("?")
# print(result)