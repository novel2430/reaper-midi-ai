import socket
import json

# 音符编号到音符名称的映射
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def note_number_to_name(note_number):
    """将 MIDI 音符编号转换为音符名称"""
    octave = (note_number // 12) - 1
    note = NOTE_NAMES[note_number % 12]
    return f"{note}{octave}"

# 服务器设置
HOST = "0.0.0.0"
PORT = 12345

# 创建 TCP 服务器
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许端口复用
server.bind((HOST, PORT))
server.listen(5)

print(f"Python 服务器启动，监听端口 {PORT}...")

while True:
    print("等待客户端连接...")
    client_socket, addr = server.accept()
    print(f"客户端已连接: {addr}")

    while True:
        try:
            # data = client_socket.recv(1024).decode().strip()
            data = client_socket.recv(1024 * 64).decode().strip()  # 解码 JSON
            if not data:
                print("客户端断开连接")
                break
            print(data)
            #json_data = json.loads(data)
            #print(json_data["type"])
            # 解析 MIDI 数据（逗号分隔的 MIDI 数字）
            # note_numbers = [int(n) for n in data.split(",") if n.isdigit()]
            # note_names = [note_number_to_name(n) for n in note_numbers]

            # print("收到 MIDI 音符:", ", ".join(note_names))

            # 回复 Lua
            client_socket.sendall("received\n".encode())

        except (ConnectionResetError, BrokenPipeError):
            print("客户端连接中断")
            break

    client_socket.close()

