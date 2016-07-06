#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        feedserver_classes
# Purpose:     Dies sind die Klassen für Feed und Feed-Item, die vom Feedserver
#              als Schnittstellenobjekte für die Worker und den Webserver ver-
#              wendet werden.
#
# Author:      akunstmann
#
# Created:     25.05.2016
# Copyright:   (c) akunstmann 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from http.server import BaseHTTPRequestHandler, HTTPServer
import __main__
import threading, re, time, logging
from os import curdir, sep

class feeditem:
    def __init__(self, feed = '', title = '', description = '', link = ''):
        self.feed = feed
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = time.strftime('%a, %d %b %Y %H:%M:%S')

class feed:
    def __init__(self, feed = '', title = '', image = '', frequency = 60, last_call = 0):
        self.feed = feed
        self.title = title
        self.image = image
        self.frequency = frequency
        self.last_call = last_call
        self.pubdate = time.strftime('%a, %d %b %Y %H:%M:%S')


class rssHandler(BaseHTTPRequestHandler):
    #Handler for the GET requests
    def do_GET(self):
        # Path parsen

        logger = __main__.logger
        logger.debug("rssHandler handels " + self.path)

        if self.path[0] == '/' and self.path[len(self.path) - 4 : len(self.path)] == '.rss':
            feed = self.path[1 : len(self.path) - 4]
            print(feed)
            outstring = ''

            for feedx in  __main__.rss_feeds:
                if feed == feedx.feed:
                    logger.debug("rssHandler prints feed " + feed + ' with ' + str(len(__main__.rss_feed_items)) + ' feed items.')
                    self.send_response(200)
                    self.send_header('Content-type','application/rss+xml')
                    self.end_headers()

                    outstring = '<?xml version="1.0" encoding="UTF-8" ?>\n'
                    outstring += '<rss version="2.0">\n'
                    outstring += '<channel>\n'
                    outstring += '<title>' + feedx.title + '</title>\n'
                    outstring += '<description>' + feedx.title + '</description>\n'
                    outstring += '<link>http://www.bahn.de/</link>\n'
                    outstring += '<pubDate>' + feedx.pubdate + ' +0200</pubDate>\n'
                    outstring += '<lastBuildDate>' + feedx.pubdate + ' +0200</lastBuildDate>\n'
                    outstring += '<image>\n'
                    outstring += '<url>' + feedx.image + '</url>\n'
                    outstring += '</image>\n'

                    for feeditem in __main__.rss_feed_items:
                        if feed == feeditem.feed:
                            outstring += '<item>\n'
                            outstring += '<title>' + feeditem.title + '</title>\n'
                            outstring += '<link><![CDATA[\n' + feeditem.link + '\n]]>\n</link>\n'
                            outstring += '<description>' + feeditem.description + '</description>\n'
                            outstring += '<pubDate>' + feeditem.pubdate + ' +0200</pubDate>\n'
                            outstring += '</item>\n'
                    outstring += '</channel>\n</rss>\n'

                    self.wfile.write(outstring.encode('utf-8'))
                    return

            if outstring == '':
                logger.debug("rssHandler could not find feed " + feed  + '.')
                self.send_response(404)
                self.send_header('Content-type','text/html')
                self.end_headers()

                # Send the html message
                outstring = "Feed " + feed + " nicht gefunden. "
                self.wfile.write(outstring.encode('utf-8'))
                return

        elif self.path[0] == '/' and self.path[len(self.path) - 4 : len(self.path)] == '.pdf':
            try:
                f = open(curdir + sep + 'vertretungsplan' +  self.path[len(self.path) - 5 : len(self.path) -4] + '.pdf', 'rb')
                self.send_response(200)
                self.send_header('Content-type', 'application/pdf')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            except IOError:
                logger.error("rssHandler could not open file " + curdir + sep + 'vertretungsplan' +  self.path[len(self.path) - 5 : len(self.path) -4] + '.pdf:' + IOError.errno)
            return

        elif self.path[0] == '/' and self.path[len(self.path) - 16 : len(self.path)] == '.rss/favicon.ico':
            # Feed-spezifisches Favicon, ggf. ist dies eine Besonderheit des Panic Statusboards, aber das ist gut, das liefert
            #print('Checkpoint 41')
            # Feed extrahieren und nachschlagen
            feed = self.path[1 : len(self.path) - 16]

            try:
                f = open(curdir + sep + feed + '.ico', 'rb')
                self.send_response(200)
                self.send_header('Content-type', 'image/x-icon')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                logger.debug("rssHandler sends " + feed + ' icon.')
            except:
                logger.debug("rssHandler could not send feed specific icon for feed " + feed + '. Sending standard icon instead.')
                try:
                    f = open(curdir + sep + 'favicon.ico', 'rb')
                    self.send_response(200)
                    self.send_header('Content-type', 'image/x-icon')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                except IOError:
                    logger.error("rssHandler could not open file " + curdir + sep + 'vertretungsplan' +  self.path[len(self.path) - 5 : len(self.path) -4] + '.pdf:' + IOError.errno)
        else:

            logger.debug("rssHandler could not find " + self.path)
            self.send_response(404)
            self.send_header('Content-type','text/html')
            self.end_headers()

            # Send the html message
            outstring = "Pfad " + self.path + " nicht gefunden. "
            self.wfile.write(outstring.encode('utf-8'))
        return

class WebserverThread(threading.Thread):
    def __init__ (self, port):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):

    	#Create a web server and define the handler to manage the
    	#incoming request
        logger = __main__.logger
        server = HTTPServer(('', self.port), rssHandler)

        logger.info('WebserverThread: Started HttpServer on port ' + str(self.port))

    	#Wait forever for incoming htto requests
        server.serve_forever()


if __name__ == '__main__':
    print('Dies ist ein Modul und nicht zur Ausführung geeignet. Bitte starten Sie feedserver_main.py.')
