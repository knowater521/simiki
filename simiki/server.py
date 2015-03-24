#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import os
import os.path
import sys
import logging
import SimpleHTTPServer
import SocketServer


URL_ROOT = None
PUBLIC_DIRECTORY = None


class Reuse_TCPServer(SocketServer.TCPServer):
    allow_reuse_address = True


class YARequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def translate_path(self, path):
        if URL_ROOT != '/' and self.path.startswith(URL_ROOT):
            if self.path == URL_ROOT or self.path == URL_ROOT + '/':
                # TODO urlparse.urljoin
                return PUBLIC_DIRECTORY + '/index.html'
            else:
                return PUBLIC_DIRECTORY + path[len(URL_ROOT):]
        else:
            return SimpleHTTPServer.SimpleHTTPRequestHandler \
                                   .translate_path(self, path)

    def do_GET(self):
        # redirect url
        if URL_ROOT != '/' and self.path == '/':
            self.send_response(301)
            self.send_header('Location', URL_ROOT)
            self.end_headers()
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


def preview(path, url_root, port=8000):
    '''
    :param path: directory path relative to current path
    :param url_root: `root` setted in _config.yml
    '''
    global URL_ROOT, PUBLIC_DIRECTORY

    if url_root != '/' and url_root.endswith('/'):
        url_root = url_root[:-1]

    URL_ROOT = url_root
    PUBLIC_DIRECTORY = os.path.join(os.getcwdu(), path)

    if os.path.exists(path):
        os.chdir(path)
    else:
        logging.error("Path {} not exists".format(path))
    try:
        Handler = YARequestHandler
        httpd = Reuse_TCPServer(("", port), Handler)
    except OSError as e:
        logging.error("Could not listen on port {0}".format(port))
        sys.exit(getattr(e, 'exitcode', 1))

    logging.info("Serving at: http://127.0.0.1:{0}{1}/".format(port, url_root))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt as e:
        logging.info("Shutting down server")
        httpd.socket.close()
