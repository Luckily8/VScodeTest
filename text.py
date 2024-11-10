# CAN总线模拟
import can
import time
import threading

# 初始化CAN总线
bus = can.interface.Bus(bustype="virtual", channel="vcan0", bitrate=50000)


# 模拟节点发送消息的函数
def send_message(node_id, msg_id, data):
    msg = can.Message(arbitration_id=msg_id, data=data, is_extended_id=False)
    try:
        bus.send(msg)
        print(f"节点 {node_id} 发送消息: {msg}")
    except can.CanError:
        print(f"节点 {node_id} 发送消息失败")


# 接收消息的函数
def receive_message():
    while True:
        msg = bus.recv(1.0)
        if msg:
            print(f"收到消息: {msg}")


# 创建并启动接收消息的线程
receiver_thread = threading.Thread(target=receive_message)
receiver_thread.daemon = True
receiver_thread.start()

# 模拟4个节点发送消息
nodes = [1, 2, 3, 4]
messages = [
    (1, 0x101, [0x11, 0x22, 0x33]),
    (2, 0x102, [0x44, 0x55, 0x66]),
    (3, 0x103, [0x77, 0x88, 0x99]),
    (4, 0x104, [0xAA, 0xBB, 0xCC]),
]

for node, msg_id, data in messages:
    send_message(node, msg_id, data)
    time.sleep(0.1)

# 保持主线程运行，以便接收消息线程可以继续运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("程序结束")
