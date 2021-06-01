import importlib
import logging
import socket
import sys
import time
import threading
import traceback

import noxitu.minecraft.protocol.proxy


LOGGER = logging.getLogger(__name__)


def listen(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen(5)

        while True:
            connection, address = server.accept()

            try:
                for name, module in list(sys.modules.items()):
                    if name.startswith('noxitu.minecraft.'):
                        importlib.reload(module)

            except:
                traceback.print_exc()
                continue

            thread = threading.Thread(target=noxitu.minecraft.protocol.proxy.handle, args=(connection, address))
            thread.daemon = True
            thread.start()


def main(host, port):
    thread = threading.Thread(target=listen, args=(host, port))
    thread.daemon = True
    thread.start()

    while True:
        time.sleep(.5)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        # filename='out.txt',
        # filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main('localhost', 25566)
