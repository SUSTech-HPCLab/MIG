from scheduler.scheduler import sheduler
import util
import socket
import queue
import threading
import os
import time
import copy
state_table = {

}



class message:
    def __init__(self, input):
        input_array = input.split(",")
        self.work_dir = input_array[0]
        self.dev = input_array[1]
        self.command = input_array[2]


class config:
    def __init__(self, ip, port, GPU_ID, MIG_Instace, Existence=False, MIG_UUID = None, Use_MPS=False, Open_MPS=False, MPS_Percentage = None):
        self.ip = ip
        self.port = port
        self.GPU_ID = GPU_ID
        self.MIG_Instace = MIG_Instace
        self.Existence = Existence
        self.MIG_UUID = MIG_UUID
        self.Use_MPS = Use_MPS
        self.Open_MPS = Open_MPS
        self.MPS_Percentage = MPS_Percentage


class manager:
    def __init__(self, sheduler, port):
        self.sheduler = sheduler
        self.job_queue = queue.Queue()
        self.lock = threading.Lock() 
        self.schedule_lock = threading.Lock() 
        self.state_table_lock = threading.Lock()
        # self.receive_input(port)
        # self.monitor_queue()
        self.schedule = {}

    def receive_input(self, port):
        def handle_client(client_socket, client_address):
            while True:
                data = client_socket.recv(1024)
                if not data:
                    print(f"Client {client_address} disconnected.")
                    break
                with self.lock:
                    self.job_queue.put(message(data.decode()))

            client_socket.close()

        def start_server():
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('0.0.0.0', port)
            server_socket.bind(server_address)
            server_socket.listen(1)
            print(f"manager server is listening on {'0.0.0.0'}:{port}...")

            while True:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
                client_thread.start()

        server_thread = threading.Thread(target=start_server)
        server_thread.start()

    def monitor_queue(self):
        def monitor():
            while True:
                with self.lock:
                    if not self.job_queue.empty():
                        with self.schedule_lock:
                            self.schedule = self.sheduler(self.job_queue)
                        self.job_queue.queue.clear()
                
                time.sleep(1)
        
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.start()
    
    def monitor_schedule(self):
        def monitor():
            while True:
                with self.schedule_lock:
                    if not self.schedule:
                        for i in self.schedule.keys():
                            value = self.schedule.get(i)
                            self.do_shecudle(i, value)
                        self.schedule = {}
                time.sleep(1)
        
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.start()
    
    def do_shecudle(self, key: message, value: config):
        worker_ip = value.ip
        worker_port = value.port
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (worker_ip, worker_port)
        client_socket.connect(server_address)
        cmd_type = 'config'
        if value.Existence:
            a = 1
            # if value.Use_MPS:
            #     if value.Open_MPS:
            #         #查询MPS服务器的PID
            #         cmd = f' CUDA_VISIBLE_DEVICES={value.MIG_UUID} && (echo get_server_list | sudo nvidia-cuda-mps-control)'
            #         client_socket.sendall(cmd.encode())
            #         mps_server_pid = client_socket.recv(1024).decode()
            #         cmd = f'echo set_active_thread_percentage {mps_server_pid} {value.MPS_Percentage} | sudo nvidia-cuda-mps-control'
            #     else:
            #         cmd = f'sudo nvidia-cuda-mps-control -d && (echo start_server -uid 1002 | sudo nvidia-cuda-mps-control) '
            #         client_socket.sendall(cmd.encode())
            #         response = client_socket.recv(1024).decode()
            #         cmd = f'echo get_server_list | sudo nvidia-cuda-mps-control'
            #         client_socket.sendall(cmd.encode())
            #         mps_server_pid = client_socket.recv(1024).decode()
            #         cmd = f'echo set_active_thread_percentage {mps_server_pid} {value.MPS_Percentage} | sudo nvidia-cuda-mps-control'
            #         client_socket.sendall(cmd.encode())
            #         response = client_socket.recv(1024).decode()
        else:
            client_socket.sendall(cmd_type.encode())
            response = client_socket.recv(1024).decode()
            CI = util.MIG_instance_map.get(value.MIG_Instace)

            cmd = "sudo nvidia-smi mig -i " + str(value.GPU_ID) + " -cgi "   + str(CI) + " -C"

            client_socket.sendall(cmd.encode())
            response = client_socket.recv(1024).decode()


            util.get_uuid()

            # value.MIG_UUID = util.get_uuid(value.ip, value.GPU_ID, value.MIG_Instace)
        

        cmd_type = 'run'
        client_socket.sendall(cmd_type.encode())
        response = client_socket.recv(1024).decode()
        cmd = f'cd {key.work_dir} && CUDA_VISIBLE_DEVICES=MIG-32522c13-1a59-5776-9d30-e0ae7b6a4874  conda run -n {key.dev} {key.command}'
        client_socket.sendall(cmd.encode())
        response = client_socket.recv(1024).decode()

        cmd_type = 'finish'
        client_socket.sendall(cmd_type.encode())
        client_socket.close()


    def state_table(self, port=11111):
        def handle_client(client_socket, client_address):
            while True:
                data = client_socket.recv(1024)
                if not data:
                    print(f"Client {client_address} disconnected.")
                    break
                with self.state_table_lock:
                    print(data.decode())
                    
            client_socket.close()

        def start_server():
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('0.0.0.0', port)
            server_socket.bind(server_address)
            server_socket.listen(1)
            print(f"manager server is listening on {'0.0.0.0'}:{port}...")

            while True:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
                client_thread.start()

        server_thread = threading.Thread(target=start_server)
        server_thread.start()


test = manager(None, 12345)

key = message('/home/zbw/MIG/schedule,Abacus,python test_program.py')
value = config(ip='172.18.36.131', port=12345, GPU_ID=0, MIG_Instace='2g.20gb')
test.state_table()
test.do_shecudle(key, value)


