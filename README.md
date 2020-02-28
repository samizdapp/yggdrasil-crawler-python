# yggdrasil-crawler-python
Small Yggdrasil network crawler with CLI, written in Python3

Based on [this script](https://github.com/Arceliar/yggdrasil-map/blob/master/scripts/crawl-dht.py)

This tool uses DHTPing in Yggdrasil Admin API to crawl through network, and then collecting NodeInfo on every available node found.
It's assumed that Admin API is available on default config sockets, like ('localhost', 9001) on Windows or "/var/run/yggdrasil.sock" on Linux. If it isn't the case, you have to change API address in yggdrasil_crawler.py. If you get 'Permission denied' on Linux, you probably should use 'sudo' to reach the socket.

crawlerclt.py is command line interface for yggdrasil_crawler.py.
