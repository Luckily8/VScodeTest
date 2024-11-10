import can
import time
import threading
import zlib

# 初始化CAN总线
bus = can.interface.Bus(bustype="virtual", channel="vcan0", bitrate=500000)


# 模拟仲裁的函数
def arbitrate(messages):
    return sorted(messages, key=lambda x: x[1])


# 计算CRC校验值的函数
def calculate_crc(data):
    return zlib.crc32(bytearray(data)) & 0xFFFFFFFF


# 模拟节点发送消息的函数
def send_message(node_id, msg_id, data):
    crc = calculate_crc(data)
    print(f"节点 {node_id} 发送消息前 CRC: {crc:08X}")

    msg = can.Message(arbitration_id=msg_id, data=data, is_extended_id=False)
    try:
        bus.send(msg)
        print(f"节点 {node_id} 发送消息: ID={msg.arbitration_id} Data={msg.data.hex()}")
    except can.CanError:
        print(f"节点 {node_id} 发送消息失败")


# 接收消息的函数
def receive_message():
    print("接收消息线程正在运行")
    while True:
        msg = bus.recv(5.0)
        if msg:
            crc = calculate_crc(msg.data)
            print(
                f"收到消息: ID={msg.arbitration_id} Data={msg.data.hex()} CRC={crc:08X}"
            )
        else:
            print("未收到消息")


# 创建并启动接收消息的线程
receiver_thread = threading.Thread(target=receive_message)
receiver_thread.daemon = True
receiver_thread.start()

print("接收消息线程已启动")
time.sleep(2)  # 增加延迟
# 模拟4个节点发送消息
nodes = [1, 2, 3, 4]
messages = [
    (1, 0x104, [0xAA, 0xBB, 0xCC]),
    (2, 0x103, [0x77, 0x88, 0x99]),
    (3, 0x102, [0x44, 0x55, 0x66]),
    (4, 0x101, [0x11, 0x22, 0x33]),
]

# 按优先级顺序发送消息
arbitrated_messages = arbitrate(messages)
for node, msg_id, data in arbitrated_messages:
    send_message(node, msg_id, data)
    time.sleep(2)  # 增加延迟

# 保持主线程运行，以便接收消息线程可以继续运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("程序结束")
