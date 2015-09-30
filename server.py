
__author__ = 'Josh Allen Bosley'

import SocketServer
import sql_settings
import request_handler

# Query information
recognized_queries = ['u', 'i', 's', 'g', 'a', 'ci']    # update, insert, select, generate

recent_queries = []
max_stored_queries = 25


class TCPConnectionHandler(SocketServer.BaseRequestHandler):

    def handle(self):

        reply = None

        # Receive data from client
        self.data = self.request.recv(sql_settings.BLOCK).split("^")

        if self.data[0] in recognized_queries:

            reply = request_handler.request_handler(self.data)

        if self.data[0] not in recognized_queries:

            reply = "?"
            sql_settings.output_update_to_screen("UNRECOGNIZED QUERY !")
            sql_settings.output_update_to_screen(self.data)


        if reply is not None:

            self.request.send(reply)

        self.request.close()


class Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)


def initiate_server_instance():

    the_server = Server((sql_settings.HOST, sql_settings.PORT), TCPConnectionHandler)
    the_server.serve_forever()

    return