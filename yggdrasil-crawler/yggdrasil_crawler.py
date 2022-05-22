import json
import socket
import sys
import time
import pprint

class YggdrasilCrawler():

  host_port = ('localhost', 9001)
  unix_socket = "/var/run/yg/yg.sock"
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
    return '{{"keepalive":true, "request":"dhtPing", "key":"{}", "coords":"{}"}}'.format(key, coords)

  def getNodeInfoRequest(self, key):
    return '{{"keepalive":true, "request":"getNodeInfo", "key":"{}"}}'.format(key)

  def getRemoteDHTRequest(self, key):
    return '{{"keepalive":true, "request":"debug_remoteGetDHT", "key":"{}"}}'.format(key)

  def doRequest(self, req):
    self.yggsocket.send(req.encode('utf-8'))
    data = json.loads(self.yggsocket.recv(1024*15))
    return data

  def handleResponse(self, address, info, data):
    self.timedout[str(address)] = {'key':str(info['key']), 'coords':str(info['coords'])}
    if not data: return
    if 'response' not in data: return
    if 'nodes' not in data['response']: return
    for addr,rumor in data['response']['nodes'].items():
      if addr in self.visited: continue
      self.rumored[addr] = rumor
    if address not in self.visited:
      self.visited[str(address)] = {'key':str(info['key']), 'coords':str(info['coords'])}
      if address in self.timedout: del self.timedout[address]

  def crawl(self):
    self.visited = dict()
    self.rumored = dict()
    self.timedout = dict()

    selfInfo = self.doRequest('{"keepalive":true, "request":"getSelf"}')

    for k,v in selfInfo['response']['self'].items(): self.rumored[k] = v
    print(f'Rumored:{len(self.rumored)}, Available: {len(self.visited)}, Timed out: {len(self.timedout)}')
    nodeInfo = self.doRequest('{"keepalive":true, "request":"getDHT"}')
    dht = nodeInfo['response']['dht']
    for ipv6,data in dht.items():
      key = data['key']
      print(f'  {ipv6}={key}')
      nodeInfo = self.doRequest(self.getRemoteDHTRequest(key))
      for k,v in nodeInfo.items():
        print(f'    {k}={v}')
      dht = nodeInfo['response']
      for ipv6,data in dht.items():
        keys = data['keys']
        for key in keys:
          print(f'  {ipv6}={key}')
          info = self.doRequest(self.getNodeInfoRequest(key))
          for k,v in info['response'].items():
            print(f' !!!! {k}={v}')
    # print("getting nodeinfo...")
    # ni_counter = 0
    # ni_max = len(self.visited)
    # for k,v in self.visited.items():
    #   ni_counter += 1
    #   print(f"{ni_counter}/{ni_max}")
    #   nodeInfo = self.doRequest(self.getNodeInfoRequest(v['key'], v['coords']))
    #   if nodeInfo['status'] == "success":
    #     self.visited[k].update(nodeInfo['response']['nodeinfo'])

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

if __name__ == "__main__":
    crawler = YggdrasilCrawler()
    crawler.crawl()
    crawler.pprint()
