import json
import socket
import sys
import time
import pprint
import os

class YggdrasilCrawler():

  host_port = ('localhost', 9001)
  unix_socket = "/var/run/yggdrasil.sock"
  yggsocket = None

  visited = dict() # Add nodes after a successful lookup response
  rumored = dict() # Add rumors about nodes to ping
  timedout = dict()

  def __init__(self, host_port=None, unix_socket=None):
    if host_port:
      self.host_port == host_port
    if unix_socket:
      self.unix_socket = unix_socket
    try:    
      self.yggsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.yggsocket.connect(self.host_port)
    except ConnectionRefusedError:
      self.yggsocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
      self.yggsocket.connect(self.unix_socket)


  def getDHTPingRequest(self, key, coords, target=None):
    return '{{"keepalive":true, "request":"dhtPing", "box_pub_key":"{}", "coords":"{}"}}'.format(key, coords)

  def getNodeInfoRequest(self, key, coords, target=None):
    return '{{"keepalive":true, "request":"getNodeInfo", "box_pub_key":"{}", "coords":"{}"}}'.format(key, coords)

  def doRequest(self, req):
    self.yggsocket.send(req.encode('utf-8'))
    data = json.loads(self.yggsocket.recv(1024*15))
    return data

  def handleResponse(self, address, info, data):
    self.timedout[str(address)] = {'box_pub_key':str(info['box_pub_key']), 'coords':str(info['coords'])}
    if not data: return
    if 'response' not in data: return
    if 'nodes' not in data['response']: return
    for addr,rumor in data['response']['nodes'].items():
      if addr in self.visited: continue
      self.rumored[addr] = rumor
    if address not in self.visited:
      self.visited[str(address)] = {'box_pub_key':str(info['box_pub_key']), 'coords':str(info['coords'])}
      if address in self.timedout: del self.timedout[address]

  def crawl(self):
    self.visited = dict()
    self.rumored = dict()
    self.timedout = dict()

    selfInfo = self.doRequest('{"keepalive":true, "request":"getSelf"}')

    for k,v in selfInfo['response']['self'].items(): self.rumored[k] = v

    while len(self.rumored) > 0:
      for k,v in self.rumored.items():
        self.handleResponse(k, v, self.doRequest(self.getDHTPingRequest(v['box_pub_key'], v['coords'])))
        break
      del self.rumored[k]
      #print(f'Rumored:{len(self.rumored)}, Available: {len(self.visited)}, Timed out: {len(self.timedout)}')

    #print("getting nodeinfo...")
    ni_counter = 0
    ni_max = len(self.visited)
    for k,v in self.visited.items():
      ni_counter += 1
      #print(f"{ni_counter}/{ni_max}")
      nodeInfo = self.doRequest(self.getNodeInfoRequest(v['box_pub_key'], v['coords']))
      if nodeInfo['status'] == "success":
        self.visited[k].update(nodeInfo['response']['nodeinfo'])

  def pprint(self):
    print(f'Timeout: ')
    for nodeaddress, nodeinfo in self.timedout.items():
      print(nodeaddress)
      for k,v in nodeinfo.items():
        print(f'  {k}={v}')

    print(f'Visited: ')
    for nodeaddress, nodeinfo in self.visited.items():
      print(nodeaddress)
      for k,v in nodeinfo.items():
        print(f'  {k}={v}')


class YggStats:
  dpc = 0
  server = 0
  hub = 0
  unknown = 0
  unavailable = 0

if __name__ == "__main__":
    crawler = YggdrasilCrawler()

    crawler.crawl()

    stats = YggStats()

    for nodeaddress, nodeinfo in crawler.timedout.items():
      stats.unavailable += 1

    for nodeaddress, nodeinfo in crawler.visited.items():
      if "name" in nodeinfo.keys():
        name = nodeinfo["name"]
        if "TAU.dpc" in name:
          stats.dpc += 1
        elif "TAU.hub" in name:
          stats.hub += 1
        elif "TAU.server" in name:
          stats.server += 1
        else:
          stats.unknown += 1
      else:
        stats.unavailable += 1

    print(f" dpc: {stats.dpc}; hub: {stats.hub}; server: {stats.server}; unknown: {stats.unknown}; unavailable: {stats.unavailable}")
    #f = open("orchestrator_stats.txt", "w")
    #f.write(f"dpc: {stats.dpc} \nhub: {stats.hub} \nserver: {stats.server} \nunknown: {stats.unknown} \nunavailable: {stats.unavailable}")
    #f.close()
