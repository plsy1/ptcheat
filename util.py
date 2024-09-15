import hashlib
import os
import bencodepy
import random


def random_peer_id():
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_.!~*()"
    ret = "-qB4660-"
    ret += "".join(random.choice(chars) for _ in range(12))
    return ret


def random_key():
    chars = "0123456789ABCDEF"
    return "".join(random.choice(chars) for _ in range(8))


def random_port():
    return random.randint(1024, 65535)


def parse_and_regenerate_torrent(filename, fake_tracker):
    with open(filename, "rb") as f:
        file_content = f.read()

    m = bencodepy.decode(file_content)

    info_value = m.get(b"info")
    if not info_value:
        raise ValueError("info field missing from torrent file")

    info_bytes = bencodepy.encode(info_value)
    info_hash = hashlib.sha1(info_bytes).hexdigest()

    info_map = dict(info_value)
    total_size = 0
    files = info_map.get(b"files")
    if not files:
        length = info_map.get(b"length")
        if length is None:
            raise ValueError("files field and length field are missing")
        total_size = length
    else:
        for file in files:
            length = file.get(b"length")
            if length is None:
                raise ValueError("length field is missing or is not an integer")
            total_size += length

    orig_announce = m.get(b"announce")
    if isinstance(orig_announce, bytes):
        orig_announce = orig_announce.decode("utf-8")

    # Handle the "announce-list" field
    announce_list = m.get(b"announce-list")
    if announce_list:
        new_announce_list = [[fake_tracker] for _ in announce_list]
        m[b"announce-list"] = new_announce_list
    else:
        # If "announce-list" is not present, replace "announce"
        m[b"announce"] = fake_tracker.encode("utf-8")
        
        
    new_torrent = bencodepy.encode(m)
    new_filename = os.path.join('torrents', f"FREE_{os.path.basename(filename)}")
    with open(new_filename, "wb") as f:
        f.write(new_torrent)

    os.remove(filename)

    return orig_announce, info_hash, total_size
