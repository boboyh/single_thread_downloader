import os
import socket
import struct
import gradio as gr
from self_class.mysocket import MySocket

def download_file(file_name : str, file_path='./Downloads', host='localhost', port=11322):
    """下载文件"""
    client_socket = MySocket()
    client_socket.connect((host, port))

    try:
        command = f'download_file:{file_name}'
        client_socket.mysend(command.encode('utf-8'))
        # 接收文件大小
        size_data = client_socket.recv_all(4)
        #size = struct.unpack('!I', size_data)[0]
        if len(size_data) != 4:
            raise ValueError(f"Expected 4 bytes for file size, but received {len(size_data)} bytes")
        size = struct.unpack('!I', size_data)[0]
        
        # 接收文件数据
        received_data = b''
        # 为什么要判断len(received_data) < size？因为recv()方法不保证一次性接收完所有数据
        while len(received_data) < size:
            chunk = client_socket.recv_all(1024)
            if not chunk:
                break
            received_data += chunk
        full_file_path = os.path.join(file_path, file_name)
        # 保存文件
        with open(full_file_path, 'wb') as f:
            f.write(received_data)
            
        print("文件下载完成")
        return full_file_path
    finally:
        client_socket.close()

def test_connection(host: str, port: int):
    client_socket = MySocket()
    try:
        client_socket.connect((host, port))
        
        # 发送命令
        command = 'get_file_list'
        client_socket.mysend(command.encode('utf-8'))
        
        # 接收文件列表
        file_list_bytes = client_socket.myreceive()
        file_list_str = file_list_bytes.decode('utf-8')
        file_list = file_list_str.split('\n')
        print(f"文件列表: {file_list}")
        file_list = [f for f in file_list if f]
        return f"<div style='color: green;'>连接成功</div>", gr.update(choices=file_list)
    except Exception as e:
        return f"<div style='color: red;'>连接失败: {e}</div>", gr.update(choices=[])
    finally:
        client_socket.close()