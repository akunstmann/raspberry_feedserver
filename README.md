# raspberry_feedserver
RSS feed generator on raspberry pi for feeding a panic status board on ios

This example shows how to download, parse and convert to rss a specific page of a website.
Framework can be extended by additional leto modules (leto = load, extract, transform, output).

Be careful about the terms of use of the website you load. Automatic reading might be forbidden. Be even more careful about the distribution of your RSS to non-private networks. Redistribution of content is probably forbidden. Do not flood websites with requests. 

Requirements
* Python3
* install Beautifulsoup first (https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* copy one of the ico files to favicon.ico

How to use
* Run feedserver_main
* Adjust times, trains and stations in leto_bahn.rss to your needs (german railway)
* Adjust highway names in auto.rss to your needs (works probably only for the south-west of germany)
* Websites are changing frequently, so you probably have to adjust the html parsing code 
* Check the results in the browser http://localhost:8080/auto.rss and http://localhost:8080/bahn.rss
* Customize the panic status board on your ipad with a rss feed panel and let it point to your RSS machine. Use ip instead of "localhost" in url.

Licence

Copyright 2016 Flightcode UG (haftungsbeschränkt), Walldorf, Germany 

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
