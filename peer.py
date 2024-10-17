from util import *
import gzip, requests, urllib, glob  # type: ignore
import os
from merge import merge_peerlists

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
    
    merge_peerlists(file_path,"all.peers")
    
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
