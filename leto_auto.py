#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        leto_auto
# Purpose:     URL konstuieren, HTML laden und parsen für definierte Verkehrs-
#              informationen für Autobahnen von der SRW3-Homepage laden.
#
# Author:      akunstmann
#
# Created:     03.06.2016
# Copyright:   (c) akunstmann 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import threading, urllib.request, collections, time, re, logging
from bs4 import BeautifulSoup
import feedserver_classes

class leto_auto(threading.Thread):
    feed = 'auto'

    strassen = [
        ['A5'],
        ['A6'],
        ['A61']
    ]


    def __init__ (self, list_feeds, list_feed_items, logger, feed = 'auto'):
        threading.Thread.__init__(self)
        self.feed_items = list_feed_items
        self.feeds = list_feeds
        self.feed = feed
        self.logger = logger
        logger.debug("leto_auto starts.")

    def run(self):

        #Erst einmal alle veralteten Feeditems aus den Feeditems löschen.
        self.feed_items[:] = [item for item in self.feed_items if (item.feed != self.feed)]

        #Url setzen und HTML herunterladen
        url = 'http://www.swr3.de/aktuell/verkehr/stauanzeige/-/id=64076/cf=42/62axcq/index.html'
        self.logger.debug('leto_auto downloads ' + url)
        html = self.download(url)

        if html is not None:
            self.logger.debug("leto_auto download successful. ")
            for strasse in self.strassen:
                #alle Daten durchgehen

                # Auseinanderlegen
                # Dies hier funktioniert leider alles nicht mehr - das Format hat sich geändert.
                #for match in html.find_all("span", class_="list-group-item"):          #Dies geht auf dem Raspberry nicht
                #for match in html.find_all("span", attrs={"class":"list-group-item"}):
                #    if match.find("strong").get_text() == strasse[0]:
                #        # Wenn sich der Abschnitt auf eine der genannten Straßen bezieht
                #        #print(match.get_text())

                #        datum = match.get_text().rpartition('[')[2]
                #        datum = datum[0:len(datum) - 2].replace('&nbsp;', ' ')
                #        datum = datum.replace('\xa0', ' ')

                #        if time.mktime(time.strptime(datum, '%d.%m.%Y %H:%M:%S')) >= time.time() - 30000:
                #            #print("Checkpoint 22")
                #            feeditem = feedserver_classes.feeditem()
                #            feeditem.feed = 'auto'
                #            title = match.get_text().rpartition('[')[0].replace('\n', '')
                #            title = title.replace('\t', '').replace('  ', ' ').replace('  ', ' ')
                #            re.sub('\s{2,}', ' ', title)
                #            feeditem.title = title
                #            print(feeditem.title)
                #            feeditem.description = match.get_text().rpartition('[')[0].replace('\n', '')
                #            feeditem.link = "http://www.swr3.de/aktuell/verkehr/aktuelle-verkehrsmeldungen/-/id=3916146/w6gc80/index.html"
                #            self.pubdate = time.strftime('%a, %d %b %Y %H:%M:%S')
                #            feeditem.pubdate = time.strftime('%a, %d %b %Y %H:%M:%S', time.strptime(datum, '%d.%m.%Y %H:%M:%S'))
                #            self.feed_items.append(feeditem)

                #Zweiter Versuch zum Parsen der Liste

                #so sieht der Source aus
                #<div id="trafficMessages">
                #<ul class="list-unstyled">
                #<li><img src="http://www.swr3.de/ext/traffic/img/construction.svg" title="" alt="" class="nocopyright"><p>A1 Trier - Saarbrücken zwischen Mehring und Hermeskeil in beiden Richtungen Fahrbahnerneuerung, es ist jeweils nur eine Spur frei. Dauer bis 10. Juli<br/><small>— seit 25.06.2016, 10:00 Uhr</small></p></li>

                try:
                    html2 = html.find(id="trafficMessages")
                    for match in html2.find_all("li"):
                        text = match.get_text()
                        if (strasse[0] + ' ') in text:      # Match für gesuchte Straße
                            datum = match.find("small").get_text().rpartition('- seit')[2][7:]
                            datum = datum.replace("Uhr", "")
                            datum = datum.replace(",", "")
                            if time.mktime(time.strptime(datum, '%d.%m.%Y %H:%M ')) >= time.time() - 30000:
                                feeditem = feedserver_classes.feeditem()
                                feeditem.feed = 'auto'
                                feeditem.title = text.replace(match.find("small").get_text(), '')
                                feeditem.link = "http://www.swr3.de/aktuell/verkehr/aktuelle-verkehrsmeldungen/-/id=3916146/w6gc80/index.html"
                                self.pubdate = time.strftime('%a, %d %b %Y %H:%M:%S')
                                feeditem.pubdate = time.strftime('%a, %d %b %Y %H:%M:%S', time.strptime(datum, '%d.%m.%Y %H:%M '))
                                self.feed_items.append(feeditem)
                                #print(feeditem.title, datum)
                            #print(match.find("small").get_text())
                except:
                    self.logger.error("leto_auto html parsing unsuccessful for " + url)


            # Jetzt noch das PubDate und den letzten Abruf setzen.
            for feed in  self.feeds:   #__main__.rss_feeds:
                if feed.feed == self.feed:
                    feed.pubdate = time.strftime('%a, %d %b %Y %H:%M:%S')
                    feed.last_call = time.time()

        return

    def download(self, url, encoding = 'utf-8'):
        try:
            response = urllib.request.urlopen(url)
            data = response.read()      # a `bytes` object
            text = data.decode(encoding)    # a `str`; this step can't be used if data is binary
            return BeautifulSoup(text, "html.parser")
            #return BeautifulSoup(urllib.request.urlopen(url).read().decode(encoding), "html.parser")

        except urllib.error.URLError as e:
            self.logger.info("leto_bahn download not successful for  " + url + ' - ' + str(e.reason))
            return None
        except urllib.error.HTTPError as e:
            self.logger.info("leto_bahn download not successful for  " + url + ' - ' + str(e.code))
            return None
        except:
            self.logger.info("leto_bahn download not successful for  " + url)
            return None

if __name__ == '__main__':
    print('Dies ist ein Modul und nicht zur Ausführung geeignet.')


