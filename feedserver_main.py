#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        feedserver_main
# Purpose:     Zentrale Komponente des Feedserver-Systems: Definiert die Feeds,
#              startet den Webserver, beherbergt die Feeditems und startet die
#              Extraktoren-Tasks.
#
# Author:      akunstmann
#
# Created:     25.05.2016
# Copyright:   (c) akunstmann 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# Hier muss ich folgende Dinge tun:
# * einen Webserver starten und auf Request die RSS ausliefern.
# * eine Liste anlegen, in der die RSS-Einträge stehen.
# * eine Timer-Schleife einbauen, die regelmäßig die Download- und Extractionsmodule anspricht.

import time, logging, sys
from http.server import HTTPServer
import feedserver_classes
import leto_bahn, leto_auto     #, leto_schule

rss_feed_items = list()
rss_feeds = list()
logger = logging.getLogger('Feedserver')

def main():

    # Dies braucht man einmal, um das Datum zu initialisieren
    time.strptime('2012-01-01', '%Y-%m-%d')

    # Logging vorbereiten
    hdlr = logging.FileHandler('feedserver.log')
    hdlr2 = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    hdlr2.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.addHandler(hdlr2)
    logger.setLevel(logging.DEBUG)

    logger.info('Main: Feedserver gestartet.')

    # Feeds vorbereiten
    rss_feeds.append(feedserver_classes.feed('bahn', 'DB Zuginformation', 'http://mediathek.deutschebahn.com/marsDB/pub/images/header_logo.png', 120, time.time()))
    rss_feeds.append(feedserver_classes.feed('auto', 'SWR Stauinformation', 'http://www.swr3.de/aktuell/verkehr/stauanzeige/-/id=64076/cf=42/62axcq/index.html', 300, time.time()))
    #rss_feeds.append(feedserver_classes.feed('schule', 'Vertretungsplan Gymnasium Walldorf', 'https://www.schulinternes.de/isis/isis-vertretungen.php', 600, time.time()))

    # Webserver starten
    rss_server = feedserver_classes.WebserverThread(8080)
    rss_server.start()

    # FeedItem-Liste füllen
    bahninfo = leto_bahn.leto_bahn(rss_feeds, rss_feed_items, logger, 'bahn')
    bahninfo.start()
    bahninfo.join()

    #schulinfo = leto_schule.leto_schule(rss_feeds, rss_feed_items, logger, 'schule')
    #schulinfo.start()
    #schulinfo.join()

    autoinfo = leto_auto.leto_auto(rss_feeds, rss_feed_items, logger, 'auto')
    autoinfo.start()
    autoinfo.join()


    # Und jetzt zyklisch durchlaufen und immer mal wieder abfragen...
    try:
        while True:
            time.sleep(10)
            for feed in rss_feeds:
                if feed.last_call + feed.frequency < time.time():
                    if feed.feed == 'bahn':
                        bahninfo = leto_bahn.leto_bahn(rss_feeds, rss_feed_items, 'bahn')
                        bahninfo.start()
                        bahninfo.join()
                    if feed.feed == 'schule':
                        #schulinfo = leto_schule.leto_schule(rss_feeds, rss_feed_items, 'schule')
                        #schulinfo.start()
                        #schulinfo.join()
                        pass
                    if feed.feed == 'auto':
                        autoinfo = leto_auto.leto_auto(rss_feeds, rss_feed_items, 'auto')
                        autoinfo.start()
                        autoinfo.join()

    except KeyboardInterrupt:
        logger.info('Main: Feedserver durch Keyboard-Interrupt beendet.')
        pass

if __name__ == '__main__':
    main()
