import threading
import time
import random

# 模拟的 CAN 总线类
class CANBus:
    def __init__(self):
        self.bus_lock = threading.Lock()
        self.current_senders = []
        self.arbitration_in_progress = False

    def request_to_send(self, node_id, msg_id):
        with self.bus_lock:
            print(f"节点 {node_id} 请求发送消息 ID: {msg_id}")
            self.current_senders.append((node_id, msg_id))

    def start_arbitration(self):
        with self.bus_lock:
            if not self.arbitration_in_progress and self.current_senders:
                self.arbitration_in_progress = True
                print("\n=== 开始仲裁过程 ===")
                # 按照消息 ID 从小到大排序，ID 越小优���级越高
                self.current_senders.sort(key=lambda x: x[1])
                print("参与仲裁的节点及其消息 ID:")
                for sender in self.current_senders:
                    print(f"  节点 {sender[0]} - 消息 ID: {sender[1]}")
                winner = self.current_senders[0]
                print(f"仲裁结果: 节点 {winner[0]} 胜出，准备发送消息 ID: {winner[1]}")
                # 通知其他节点仲裁结果
                losers = self.current_senders[1:]
                self.current_senders = []
                self.arbitration_in_progress = False
                return winner, losers
            else:
                return None, None

# 模拟的 CAN 节点类
class CANNode(threading.Thread):
    def __init__(self, node_id, bus):
        super().__init__()
        self.node_id = node_id
        self.bus = bus
        self.running = True

    def run(self):
        while self.running:
            # 随机等待一段时间再尝试发送
            time.sleep(random.uniform(0.5, 1.0))
            msg_id = random.randint(0x100, 0x1FF)
            self.bus.request_to_send(self.node_id, msg_id)
            # 等待一小段时间以便总线收集请求
            time.sleep(0.2)
            winner, losers = self.bus.start_arbitration()
            if winner:
                if winner[0] == self.node_id:
                    self.send_message(msg_id)
                elif any(loser[0] == self.node_id for loser in losers):
                    print(f"节点 {self.node_id} 仲裁失败，等待下一次发送")
            else:
                # 仲裁尚未开始或没有胜出
                pass

    def send_message(self, msg_id):
        print(f"节点 {self.node_id} 正在发送消息 ID: {msg_id}")
        # 模拟发送时间
        time.sleep(0.1)
        print(f"节点 {self.node_id} 完成消息 ID: {msg_id} 的发送\n")

    def stop(self):
        self.running = False

# 主程序
if __name__ == "__main__":
    bus = CANBus()
    nodes = []

    # 创建节点
    for i in range(4):
        node = CANNode(i + 1, bus)
        nodes.append(node)

    # 启动所有节点线程
    for node in nodes:
        node.start()

    try:
        # 运行一段时间后停止
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        for node in nodes:
            node.stop()
        for node in nodes:
            node.join()
        print("模拟结束。")
