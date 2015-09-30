__author__ = 'jbosley2'
import threading
import server as server_

if __name__ == '__main__':

    threads = []

    # Start Node-Server Thread
    server_thread = threading.Thread(target=server_.initiate_server_instance)
    threads.append(server_thread)
    server_thread.start()
