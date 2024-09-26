import sys
sys.path.append('/home/zbw/MIG/MIG_Schedule')

import subprocess
import socket
import threading
import subprocess
import re
import os
import util.util
class Worker:
    def __init__(self, port):
        self.port = port
        worker_thread = threading.Thread(target=self.receive_and_send_message, args=('0.0.0.0', self.port))
        worker_thread.start()
        uuid_thread = threading.Thread(target=self.return_uuid, args=(22222,))
        uuid_thread.start()

    def receive_and_send_message(self, server_ip, server_port):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('0.0.0.0', server_port)
        server_socket.bind(server_address)
        server_socket.listen(1)
        print(f"worker is listening on {server_ip}:{server_port}...")

        while True:
            client_socket, client_address = server_socket.accept()
            while True:
                data = client_socket.recv(1024)
                if not data:
                    print(f"Client {client_address[0]}:{client_address[1]} disconnected.")
                    break
                received_message = data.decode()
                if received_message == 'config':
                    response_message = 'okk'
                    client_socket.sendall(response_message.encode())

                    data = client_socket.recv(1024)
                    received_message = data.decode()
                    
                    result = subprocess.check_output(received_message, shell=True)
                    result = result.decode().strip()

                    if result == '':
                        result = 'finish'
                    GI_ID = util.get_GI_ID(result)
                    if GI_ID:
                        result = GI_ID
                    response_message = result

                    client_socket.sendall(response_message.encode())
            

                if received_message == 'run':

                    response_message = 'okk'
                    client_socket.sendall(response_message.encode())
                    data = client_socket.recv(1024)
                    received_message = data.decode()
      
                    def execute_command(command):
                        commands = command.split(",")
                        cmd = ''
                        if commands[1] == 'Y':
                            CUDA_MPS_PIPE_DIRECTORY = f'/tmp/{commands[0]}-pipe'
                            CUDA_MPS_LOG_DIRECTORY=f'/tmp/{commands[0]}-log'

                            cmd=f'cd /home/zbw/MIG/MIG_Schedule/schedule && export CUDA_MPS_PIPE_DIRECTORY={CUDA_MPS_PIPE_DIRECTORY} && export CUDA_MPS_LOG_DIRECTORY={CUDA_MPS_LOG_DIRECTORY} && CUDA_VISIBLE_DEVICES={commands[0]}  python warm.py'
                            result = subprocess.check_output(cmd, shell=True)

                            cmd = f'export CUDA_MPS_PIPE_DIRECTORY={CUDA_MPS_PIPE_DIRECTORY} && export CUDA_MPS_LOG_DIRECTORY={CUDA_MPS_LOG_DIRECTORY} && export CUDA_VISIBLE_DEVICES={commands[0]} && (echo get_server_list | sudo -E nvidia-cuda-mps-control)'
                            pid = subprocess.check_output(cmd, shell=True)
                            pid = pid.decode().strip()

                            # cmd = f'export CUDA_MPS_PIPE_DIRECTORY={CUDA_MPS_PIPE_DIRECTORY} && export CUDA_MPS_LOG_DIRECTORY={CUDA_MPS_LOG_DIRECTORY} && echo set_active_thread_percentage {pid} {commands[5]} | sudo -E nvidia-cuda-mps-control && cd {commands[2]} && CUDA_VISIBLE_DEVICES={commands[0]}  conda run -n {commands[3]} {commands[4]}'
                            cmd = f'export CUDA_MPS_PIPE_DIRECTORY={CUDA_MPS_PIPE_DIRECTORY} && export CUDA_MPS_LOG_DIRECTORY={CUDA_MPS_LOG_DIRECTORY} && echo set_active_thread_percentage {pid} {commands[5]} | sudo -E nvidia-cuda-mps-control && cd {commands[2]} && CUDA_VISIBLE_DEVICES={commands[0]}  {commands[4]}'
                            result = subprocess.check_output(cmd, shell=True)
                        else:
                            # cmd = f'cd {commands[2]} && CUDA_VISIBLE_DEVICES={commands[0]}  conda run -n {commands[3]} {commands[4]}'
                            cmd = f'cd {commands[2]} && CUDA_VISIBLE_DEVICES={commands[0]}  {commands[4]}'
                            result = subprocess.check_output(cmd, shell=True)


                        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        server_address = ('172.18.36.119', 11111)
                        client_socket.connect(server_address)

                        cuda_visible_devices = cmd.split('CUDA_VISIBLE_DEVICES=')[1].split()[0]
                        state_change = f'{cuda_visible_devices},{command}'

                        client_socket.sendall(state_change.encode())
                        client_socket.close()

                    
                    command_thread = threading.Thread(target=execute_command, args=(received_message,))
                    command_thread.start()

                    response_message = 'okk'
                    client_socket.sendall(response_message.encode())


    def return_uuid(self, server_port=22222):
        def execute_command(command):
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout.strip() 
            return output
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('0.0.0.0', server_port)
        server_socket.bind(server_address)
        server_socket.listen(1)
        print(f"uuid_server is listening on 0.0.0.0:{server_port}...")
        while True:
            client_socket, client_address = server_socket.accept()
            data = client_socket.recv(1024)
            received_message = data.decode()
            result = execute_command(received_message)

            client_socket.sendall(result.encode())
            client_socket.close()

test = Worker(12345)
    