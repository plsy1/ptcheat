import bencodepy
import struct


def decode_peerlist_from_bencode(data):
    try:
        # 解码 bencoded 数据
        decoded_data = bencodepy.decode(data)

        # 打印解码后的数据结构
        print("Decoded data structure:", decoded_data)

        # 提取 peer 列表
        peers = []
        peers_compact = decoded_data.get(b'peers', b"")

        # 输出 peers_compact 的类型
        print(f"Type of 'peers': {type(peers_compact)}")

        if isinstance(peers_compact, bytes):
            # 解析字节串以提取 IP 和端口
            for i in range(0, len(peers_compact), 6):
                ip_bytes = peers_compact[i:i + 4]
                port_bytes = peers_compact[i + 4:i + 6]

                if len(ip_bytes) < 4 or len(port_bytes) < 2:
                    break  # 如果字节不足，则跳出

                # 解析 IP 和端口
                ip_str = ".".join(str(b) for b in ip_bytes)
                port_num = struct.unpack("!H", port_bytes)[0]

                peers.append(f"{ip_str}:{port_num}")

        elif isinstance(peers_compact, list):
            for peer_entry in peers_compact:
                # 每个 peer_entry 应该是一个字典，包含 IP 和端口
                if isinstance(peer_entry, dict):
                    ip = peer_entry.get(b'ip')
                    port = peer_entry.get(b'port')

                    if isinstance(ip, bytes) and isinstance(port, int):
                        ip_str = ip.decode('utf-8')
                        peers.append(f"{ip_str}:{port}")
                    else:
                        print(f"Warning: Invalid peer entry format: {peer_entry}")

        else:
            print("Warning: 'peers' is not a recognized format.")
            return None
        
        return peers
    except Exception as e:
        print(f"Error decoding peer list: {e}")
        return None


def read_peerlist(filename):
    try:
        with open(filename, "rb") as file:
            # 读取文件数据
            data = file.read()
            # 调用解码函数
            decoded_peers = decode_peerlist_from_bencode(data)
            print("\nDecoded peer list:")
            for peer in decoded_peers:
                print(peer)
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")


# 指定文件名
filename = ""

# 调用读取函数
read_peerlist(filename)