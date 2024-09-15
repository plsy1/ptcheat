import argparse, uvicorn
from server import App
from peer import getPeer
from starlette.middleware.wsgi import WSGIMiddleware

def main():
    parser = argparse.ArgumentParser(description='Process some commands.')
    parser.add_argument('-G', action='store_true', help='Execute getPeer function')
    parser.add_argument('-S', action='store_true', help='Run the Flask application')
    args = parser.parse_args()

    if args.G:
        getPeer()
    elif args.S:
        asgi_app = WSGIMiddleware(App)
        Config = uvicorn.Config(asgi_app, host="0.0.0.0", port=54321, log_level="info", reload=False,)
        Server = uvicorn.Server(Config)
        Server.run()
    else:
        print("No valid argument provided. Use -G to execute getPeer or -S to run the Flask app.")

if __name__ == "__main__":
    main()
