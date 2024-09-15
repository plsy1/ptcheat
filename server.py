import urllib, binascii,os
from flask import Flask, request, send_file  # type: ignore


App = Flask(__name__)


@App.route("/announce", methods=["GET"])
def foo():
    try:
        info_hash = request.args.get("info_hash", "")
        info_hash_bytes = urllib.parse.unquote_to_bytes(info_hash)
        hex_info_hash = binascii.hexlify(info_hash_bytes).decode()
        
        filename = f"{hex_info_hash}.peers"
        file_path = os.path.join('torrents', filename)
        return send_file(file_path, mimetype="application/octet-stream")

    except Exception as e:
        return f"Error: {e}"

@App.route("/announce2", methods=["GET"])
def bar():
    try:
        filename = "all_peers.peers"
        return send_file(filename, mimetype="application/octet-stream")

    except Exception as e:        
        return f"Error: {e}"
