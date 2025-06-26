import asyncio
import websockets
import json
import random
import time

# 初始化参数
parameters = {
    "ip": "192.168.1.1",
    "port": 8080,
    "pre_lidar_ip": "192.168.1.2",
    "pre_lidar_port": 8081,
    "speed": 100,
    "angle": 20
}

# 生成测试数据
def generate_test_data():
    test_data = {
        "ip": f"192.168.1.{random.randint(1, 254)}",
        "port": random.randint(1, 65535),
        "angle": round(random.uniform(0, 360), 1),
        "speed": random.randint(0, 10000),
        "temperature": round(random.uniform(-50, 200), 1),
        "pressure": round(random.uniform(0, 10), 2),
        "humidity": round(random.uniform(0, 100), 1),
        "brightness": random.randint(0, 100),
        "volume": random.randint(0, 100),
        "timeout": random.randint(1, 3600)
    }
    return test_data

# 定时发送测试数据
async def send_test_data(websocket):
    while True:
        try:
            test_data = generate_test_data()
            message = {
                "type": "data",
                "data": test_data
            }
            await websocket.send(json.dumps(message))
            await asyncio.sleep(5)  # 每 5 秒发送一次
        except websockets.exceptions.ConnectionClosedOK:
            break
        except Exception as e:
            print(f"发送测试数据出错: {e}")
            break

# 处理客户端连接
async def handle_client(websocket, path):
    try:
        print("客户端已连接")
        # 启动发送测试数据的任务
        # send_task = asyncio.create_task(send_test_data(websocket))

        while True:
            # 接收客户端消息
            message = await websocket.recv()
            try:
                data = json.loads(message)
                if data.get("command") == "read":
                    # 处理读取参数请求
                    response = {
                        "type": "data",
                        "data": parameters
                    }
                    await websocket.send(json.dumps(response))
                elif data.get("command") == "write":
                    # 处理写入参数请求
                    new_params = data.get("data", {})
                    # 打印接收到的数据
                    print(f"接收到的写入参数数据: {new_params}")
                    parameters.update(new_params)
                    response = {
                        "type": "response",
                        "success": True
                    }
                    await websocket.send(json.dumps(response))
                else:
                    # 处理未知命令
                    response = {
                        "type": "response",
                        "success": False,
                        "error": "未知命令"
                    }
                    await websocket.send(json.dumps(response))
            except json.JSONDecodeError:
                # 处理 JSON 解析错误
                response = {
                    "type": "response",
                    "success": False,
                    "error": "无效的 JSON 数据"
                }
                await websocket.send(json.dumps(response))
    except websockets.exceptions.ConnectionClosedOK:
        print("客户端连接正常关闭")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print("客户端已断开连接")

# 启动 WebSocket 服务器
start_server = websockets.serve(handle_client, "172.28.0.208", 9002)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()