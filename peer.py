from util import *
import gzip, requests, urllib, glob  # type: ignore
import bencodepy
import struct
import os

def decode_peerlist_from_bencode(data):
    try:
        # Decode the bencoded data
        decoded_data = bencodepy.decode(data)
        
        # Extract the peer list
        peers_compact = decoded_data.get(b'peers', b'')
        
        return peers_compact
    except Exception as e:
        print(f"Error decoding peer list: {e}")
        return b''

def encode_peerlist_to_bencode(peers_compact):
    try:
        # Ensure peers_compact is bytes-like
        if isinstance(peers_compact, list):
            # Combine list of bytes into a single bytes object
            peers_compact = b''.join(peers_compact)
        
        # Create a dictionary with the peers data
        bencoded_data = bencodepy.encode({b'peers': peers_compact})
        return bencoded_data
    except Exception as e:
        print(f"Error encoding peer list: {e}")
        return b''

def parse_peers(peers_compact):
    # Extract peers as a list of (ip, port) tuples
    peers = []
    while peers_compact:
        ip = peers_compact[:4]
        port = struct.unpack('>H', peers_compact[4:6])[0]
        peers.append((ip, port))
        peers_compact = peers_compact[6:]
    return peers

def serialize_peers(peers):
    # Serialize (ip, port) tuples into compact form
    peers_compact = b''
    for ip, port in peers:
        peers_compact += ip + struct.pack('>H', port)
    return peers_compact

def merge_and_deduplicate_peerlists(file1, file2, output_file):
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            data1 = f1.read()
            data2 = f2.read()
            
            # Decode the peer lists from both files
            peers_compact1 = decode_peerlist_from_bencode(data1)
            peers_compact2 = decode_peerlist_from_bencode(data2)
            
            # Parse the peers data into (ip, port) tuples
            peers1 = parse_peers(peers_compact1)
            peers2 = parse_peers(peers_compact2)
            
            # Combine and deduplicate peers
            all_peers = set(peers1 + peers2)
            
            # Serialize the deduplicated peers back to compact form
            combined_peers_compact = serialize_peers(all_peers)
            
            # Encode the combined peers list back to bencode format
            combined_bencoded_data = encode_peerlist_to_bencode(combined_peers_compact)
            
            # Save the combined data to a new file
            with open(output_file, 'wb') as out_file:
                out_file.write(combined_bencoded_data)
                
            print(f"Successfully merged and deduplicated peer lists into {output_file}.")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def update_all_peers_with_new_peerlist(new_peerlist, filename='all_peers.peers'):
    try:
        if os.path.exists(filename):
            # If the file exists, read the existing data
            with open(filename, 'rb') as file:
                existing_data = file.read()
            
            # Decode existing data and new data
            existing_peers_compact = decode_peerlist_from_bencode(existing_data)
            new_peers_compact = decode_peerlist_from_bencode(new_peerlist)
            
            # Parse peers
            existing_peers = parse_peers(existing_peers_compact)
            new_peers = parse_peers(new_peers_compact)
            
            # Combine and deduplicate peers
            all_peers = set(existing_peers + new_peers)
            
            # Serialize the deduplicated peers back to compact form
            combined_peers_compact = serialize_peers(all_peers)
            
            # Encode the combined peers list back to bencode format
            combined_bencoded_data = encode_peerlist_to_bencode(combined_peers_compact)
            
            # Write back to the file
            with open(filename, 'wb') as file:
                file.write(combined_bencoded_data)
            
            print(f"Updated {filename} with new peer list.")
        else:
            # If the file does not exist, create it and write the new peer list
            with open(filename, 'wb') as file:
                file.write(new_peerlist)
            
            print(f"Created {filename} and wrote new peer list.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def request_tracker(tracker_url, info_hash_hex, init_size):
    try:
        port = random_port()
        filename = f"{info_hash_hex}.peers"
        file_path = os.path.join('torrents', filename)
        info_hash = bytes.fromhex(info_hash_hex)
        info_hash_encoded = urllib.parse.quote_from_bytes(info_hash)

        peer_id = random_peer_id()
        key = random_key()

        req_url = (
            f"{tracker_url}&info_hash={info_hash_encoded}&peer_id={peer_id}&port={port}&uploaded=0"
            f"&downloaded=0&left={init_size}&corrupt=0&key={key}&event=started&numwant=200&compact=1"
            f"&no_peer_id=1&supportcrypto=1&redundant=0"
        )

        headers = {
            "User-Agent": "qBittorrent/4.6.6",
            "Accept-Encoding": "gzip",
            "Connection": "close",
        }

        print("Requesting:", req_url)
        try:
            response = requests.get(req_url, headers=headers, stream=True)
            response.raise_for_status()
        except Exception as e:
            print("Error while request tracker:", e)
            return

        if response.headers.get("Content-Encoding") == "gzip":
            with gzip.GzipFile(fileobj=response.raw) as reader:
                body = reader.read()
        else:
            body = response.content

        with open(file_path, "wb") as file:
            file.write(body)

    except Exception as e:
        print("Error while request tracker:", e)
        return

    print(f"Data successfully written to {file_path}")
    
    new_peerlist = open(file_path, 'rb').read()
    update_all_peers_with_new_peerlist(new_peerlist)


def getPeer():
    for file_path in glob.glob(os.path.join('torrents', "*.torrent")):
        if os.path.basename(file_path).startswith("FREE_"):
            print("Skipping already processed torrent:", file_path)
            continue
        print("Processing:", file_path)
        real_announce, hash, left_size = parse_and_regenerate_torrent(
            file_path, "http://127.0.0.1:54321/announce"
        )
        print(f"info_hash: {hash}, size: {left_size}")

        request_tracker(real_announce, hash, left_size)
