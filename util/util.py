
import subprocess
import socket
from itertools import product
import re

config_list = [[7], [4,3], [4,2,1], [4,1,1,1], [3,3], [3,2,1], [3,1,1,1],[2,2,3], [2,1,1,3], [1,1,2,3], [1,1,1,1,3], [2,2,2,1], [2,1,1,2,1],[1,1,2,2,1],[2,1,1,1,1,1],
                   [1,1,2,1,1,1], [1,1,1,1,2,1], [1,1,1,1,1,2], [1,1,1,1,1,1,1]]
class table_value:
    def __init__(self, ip, port, GPU_ID, MIG_config, GI_ID, job_list=[]):
        self.ip = ip
        self.port = port
        self.GPU_ID = GPU_ID
        self.MIG_config = MIG_config
        self.job_list = job_list
        self.GI_ID = GI_ID

    def __str__(self):
        attributes = vars(self)
        attr_str = ""
        for attr, value in attributes.items():
            attr_str += f"{attr}: {value}\n"
        return attr_str

MIG_instance_map = {
    '1g.10gb': 19,
    '2g.20gb': 14,
    '3g.40gb': 9,
    '4g.40gb': 5,
    '7g.80gb': 0,
}


Map_table = {

}
def execute_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout.strip() 
    return output

def get_uuid(ip, port, GPU_ID, MIG_Instace):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = (ip, port)
    client_socket.connect(server_address)

    message = "nvidia-smi -L"
    client_socket.sendall(message.encode())
    uuid = client_socket.recv(1024).decode()
    client_socket.close()
    lines = uuid.splitlines()  # 将多行文本分割成行
    uuid_list = []
    for line in lines:
        if MIG_Instace in line:
            uuid_list.append(re.search(r"UUID:\s*([a-zA-Z0-9\-]+)", line).group(1))
    return uuid_list


def get_GI_ID(input):
    pattern = r"GPU instance ID\s*(\d+)"
    match = re.search(pattern, input)
    if match:
        gpu_instance_id = match.group(1)
        return gpu_instance_id
    else:
        return None
    



def create_instance(config, ip=0, GPU=0):
    CI = MIG_instance_map.get(config)
    result = execute_command("sudo nvidia-smi mig -i " + str(GPU) + " -cgi "   + str(CI) + " -C")
    print(result)
    return CI

def destory_instance(table_value: table_value):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (table_value.ip, table_value.port)
    client_socket.connect(server_address)

    cmd_type = 'config'
    client_socket.sendall(cmd_type.encode())
    response = client_socket.recv(1024).decode()


    message = f"sudo nvidia-smi mig -dci -i {table_value.GPU_ID} -gi {table_value.GI_ID} -ci 0 && sudo nvidia-smi mig -dgi -i  {table_value.GPU_ID} -gi {table_value.GI_ID}"
    client_socket.sendall(message.encode())
    response = client_socket.recv(1024).decode()

    client_socket.close()


def MIG_check(config):
    # return support config
    global config_list
    
    if config in config_list:
        return True
    else:
        return False


def get_MIG_config():
    global config_list
    return config_list



