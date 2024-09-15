import bencodepy
import struct


# Function to decode peer list from bencode format
def decode_peerlist_from_bencode(data):
    try:
        # Decode the bencoded data
        decoded_data = bencodepy.decode(data)

        # Extract the peer list
        peers_compact = decoded_data.get(b"peers", b"")

        # Ensure the peers data is a multiple of 6 bytes
        if len(peers_compact) % 6 != 0:
            raise ValueError(
                f"Invalid peers length: {len(peers_compact)} (should be multiple of 6)"
            )

        peers = []
        for i in range(0, len(peers_compact), 6):
            ip_bytes = peers_compact[i : i + 4]
            port_bytes = peers_compact[i + 4 : i + 6]
            # Convert IP and port from binary to human-readable form
            ip_str = ".".join(map(str, ip_bytes))
            port_num = struct.unpack("!H", port_bytes)[
                0
            ]  # Port is in network byte order

            peers.append(f"{ip_str}:{port_num}")

        return peers
    except Exception as e:
        print(f"Error decoding peer list: {e}")
        return []


# Function to read and decode peer list
def read_peerlist(filename):
    try:
        with open(filename, "rb") as file:
            data = file.read()
            print("Raw peer list data:")
            print(data)

            decoded_peers = decode_peerlist_from_bencode(data)
            print("\nDecoded peer list:")
            for peer in decoded_peers:
                print(peer)
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")


filename = "all_peers.peers"

read_peerlist(filename)
