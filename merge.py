import bencodepy
import struct
import os
import logging
from collections import OrderedDict
from typing import List, Optional, Dict, Union

# 配置日志
logging.basicConfig(level=logging.INFO)

def decode_peerlist_from_bencode(data: bytes) -> Optional[List[Dict[str, Union[str, int]]]]:
    """Decode a peer list from bencoded data."""
    try:
        decoded_data = bencodepy.decode(data)
        peers = []
        peers_compact = decoded_data.get(b'peers', b"")
        logging.info("Type of 'peers': %s", type(peers_compact))

        if isinstance(peers_compact, bytes):
            peers = parse_compact_peer_list(peers_compact)
        elif isinstance(peers_compact, list):
            peers = parse_list_peer_list(peers_compact)
        else:
            logging.warning("'peers' is not a recognized format.")
            return None
        return peers
    except Exception as e:
        logging.error("Error decoding peer list: %s", e)
        return None

def parse_compact_peer_list(peers_compact: bytes) -> List[Dict[str, Union[str, int]]]:
    """Parse compact peer list from bytes."""
    peers = []
    for i in range(0, len(peers_compact), 6):
        ip_bytes = peers_compact[i:i + 4]
        port_bytes = peers_compact[i + 4:i + 6]

        if len(ip_bytes) < 4 or len(port_bytes) < 2:
            break  

        ip_str = ".".join(str(b) for b in ip_bytes)
        port_num = struct.unpack("!H", port_bytes)[0]
        peers.append({'ip': ip_str, 'port': port_num}) 
    return peers

def parse_list_peer_list(peers_compact: list) -> List[Dict[str, Union[str, int]]]:
    """Parse peer list from a list of dictionaries."""
    peers = []
    for peer_entry in peers_compact:
        if isinstance(peer_entry, dict):
            ip = peer_entry.get(b'ip')
            port = peer_entry.get(b'port')

            if isinstance(ip, bytes) and isinstance(port, int):
                ip_str = ip.decode('utf-8')
                peers.append({'ip': ip_str, 'port': port})
            else:
                logging.warning("Invalid peer entry format: %s", peer_entry)
    return peers

def save_peers_as_bencoded(peers: List[Dict[str, Union[str, int]]], output_file: str, complete: int, incomplete: int, interval: int, min_interval: int) -> None:
    """Save the peer list as Bencoded format."""

    peer_dict = {
        b'complete': complete,
        b'incomplete': incomplete,
        b'interval': interval,
        b'min interval': min_interval,
        b'peers': peers,
    }
    

    bencoded_data = bencodepy.encode(peer_dict)

    with open(output_file, 'wb') as out_file:
        out_file.write(bencoded_data)

    logging.info("Successfully saved peers as Bencoded format in %s.", output_file)

def load_existing_peers(output_file: str) -> List[Dict[str, Union[str, int]]]:
    """Load existing peers from the output file if it exists."""
    if os.path.exists(output_file):
        with open(output_file, 'rb') as f:
            data = f.read()
            existing_peers = decode_peerlist_from_bencode(data)
            return existing_peers if existing_peers else []
    return []

def merge_peerlists(file1: str, output_file: str) -> None:
    """Merge peer list from file1 into all (output_file) and save as Bencoded format."""
    peers_set = OrderedDict()  
    
    complete = 0  
    incomplete = 0
    interval = 2700  
    min_interval = 45  

    existing_peers = load_existing_peers(output_file)
    
    for peer in existing_peers:
        peers_set[(peer['ip'], peer['port'])] = peer

    try:
        with open(file1, 'rb') as f1:
            data1 = f1.read()
            peers1 = decode_peerlist_from_bencode(data1)
            if peers1:
                for peer in peers1:
                    peers_set[(peer['ip'], peer['port'])] = peer

        save_peers_as_bencoded(list(peers_set.values()), output_file, complete, incomplete, interval, min_interval)

    except FileNotFoundError as e:
        logging.error("File not found: %s", e)
    except Exception as e:
        logging.error("An error occurred: %s", e)
