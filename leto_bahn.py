#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        bahninfo_loader
# Purpose:     URL konstuieren, HTML laden und parsen für definierte Verspätungs-
#              informationen für Züge von der Bahn-Website.
#
# Author:      akunstmann
#
# Created:     25.05.2016
# Copyright:   (c) akunstmann 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import threading, urllib.request, collections, time, logging
from bs4 import BeautifulSoup
import feedserver_classes

class leto_bahn(threading.Thread):
    feed = 'bahn'

    zuege = [
        ['04:44', '06:44', 'Wiesloch-Walldorf', 'IC 2278'],
        ['05:36', '07:36', 'Wiesloch-Walldorf', 'IC 2376'],
        ['07:35', '09:35', 'Wiesloch-Walldorf', 'IC 2374'],
        ['09:39', '11:39', 'Mannheim', 'RE 4564'],
        ['11:35', '13:35', 'Wiesloch-Walldorf', 'IC 2270'],
        ['13:35', '15:35', 'Wiesloch-Walldorf', 'IC 2276'],
        ['15:20', '17:20', 'Frankfurt(Main)Hbf', 'IC 2373'],
        ['16:20', '18:20', 'Frankfurt(Main)Hbf', 'IC 2295'],
        ['17:20', '19:20', 'Frankfurt(Main)Hbf', 'IC 2375'],
        ['18:20', '20:20', 'Frankfurt(Main)Hbf', 'IC 2397'],
        ['19:51', '21:50', 'Frankfurt(Main)Hbf', 'ICE 1093'],
        ['20:13', '22:13', 'Frankfurt(Main)Hbf', 'ICE 273'],
        ['21:08', '23:08', 'Frankfurt(Main)Hbf', 'ICE 1593'],
    ]


    def __init__ (self, list_feeds, list_feed_items, logger, feed = 'bahn'):
        threading.Thread.__init__(self)
        self.feed_items = list_feed_items
        self.feeds = list_feeds
        self.feed = feed
        self.logger = logger
        self.logger.debug("leto_bahn starts.")

    def run(self):
        #print('Checkpoint 20')
        #Erst einmal alle veralteten Feeditems aus den Feeditems löschen.
        self.feed_items[:] = [item for item in self.feed_items if (item.feed != self.feed)]

        for zug in self.zuege:
        #alle Daten durchgehen
            if time.localtime() >= time.strptime(time.strftime('%Y-%m-%d ') + zug[0],'%Y-%m-%d %H:%M') and time.localtime() <= time.strptime(time.strftime('%Y-%m-%d ') + zug[1],'%Y-%m-%d %H:%M'):
                #aktuelle Züge abrufen und durchsuchen

                #print(zug[0] + ' - ' + zug[1] + ' ist aktuell: ' + zug[3] + ' ab ' + zug[2] + ':')
                url = 'http://reiseauskunft.bahn.de/bin/bhftafel.exe/dn?rt=1&input=' + zug[2] + '&time=' + zug[0] + '+120&date=' +  time.strftime('%d.%m.%Y') + '&productsFilter=1111100000&start=1&boardType=dep&maxJourneys=&REQTrain_name=' + urllib.parse.quote(zug[3])
                self.logger.debug("leto_bahn downloads " + url)

                html = self.download(url)

                if html is not None:
                    self.logger.debug("leto_bahn download successful. ")
                    # Auseinanderlegen

                    try:

                        # Hier leide ich darunter, dass die Zeile immer mal journeyRow_1 oder journeyRow_0 heißt.
                        if html.find(id="journeyRow_0"):
                            ids = "journeyRow_0"
                        elif html.find(id="journeyRow_1"):
                            ids = "journeyRow_1"

                        # Zum RSS-Feed-Item zusammensetzen
                        feeditem = feedserver_classes.feeditem()
                        feeditem.feed = 'bahn'
                        #feeditem.title = zug[3] + ' von ' + zug[2] + ' nach ' + html.find(id=ids).find("td", class_="route").find("a").get_text().strip() + ': ' + html.find(id=ids).find("td", class_="time").get_text().strip() + ' ' + html.find(id=ids).find("td", class_="ris").get_text().strip().replace('\n', ' ')
                        feeditem.title = zug[3] + ' von ' + zug[2] + ' nach ' + html.find(id=ids).find("td", attrs = {"class":"route"}).find("a").get_text().strip() + ': ' + html.find(id=ids).find("td", attrs = {"class":"time"}).get_text().strip() + ' ' + html.find(id=ids).find("td", attrs = {"class":"ris"}).get_text().strip().replace('\n', ' ')
                        #feeditem.description = html.find(id=ids).find("td", class_="time").get_text().strip() + ' ' + html.find(id=ids).find("td", class_="ris").get_text().strip().replace('\n', ' ')
                        #feeditem.link = html.find(id=ids).find("td", class_="train").find("a")['href']
                        feeditem.link = html.find(id=ids).find("td", attrs={"class":"train"}).find("a")['href']
                        self.feed_items.append(feeditem)

                    except:
                        self.logger.error("leto_bahn html parsing unsuccessful for " + url)

            # Jetzt noch das PubDate und den letzten Abruf setzen.
            for feed in  self.feeds:
                if feed.feed == self.feed:
                    feed.pubdate = time.strftime('%a, %d %b %Y %H:%M:%S')
                    feed.last_call = time.time()

        return

    def download(self, url, encoding = 'ISO-8859-1'):
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
