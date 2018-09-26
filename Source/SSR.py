#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import json
import urllib

class Client:

  httpClient = None
  LIST_SERVER='/servers'
  CUR_SERVER='/current'
  STATUS='/status'
  MODE='/mode'
  MODES=['auto','global','manual']

  def __init__(self):
    self.httpClient = httplib.HTTPConnection('localhost', 9528, timeout=30)

  def _get(self, url):
    try:
      self.httpClient.request('GET', url)
      res = self.httpClient.getresponse()
      return res if res.status == 200 and res.reason == 'OK' else False
    except Exception, e:
      return False

  def _post(self, url, parma):
    try:
      params = urllib.urlencode(parma)
      headers = {'Content-type': 'application/x-www-form-urlencoded'
                     , 'Accept': 'text/plain'}
      self.httpClient.request('PUT', url, params, headers)
      res = self.httpClient.getresponse()
      return res if res.status == 200 and res.reason == 'OK' else False
    except Exception, e:
      return False

  def _parseArgs(self, str):
    return str.split(':', 2);

  def _getServers(self):
    res = self._get(self.LIST_SERVER)
    if res:
      return json.loads(res.read())
    return []

  def _getCurrentServer(self):
    res = self._get(self.CUR_SERVER)
    if res:
      return json.loads(res.read())
    return []


  def _getStatus(self):
    res = self._get(self.STATUS)
    if res:
      data = json.loads(res.read())
      return data['Enable']
    return False

  def _getMode(self):
    res = self._get(self.MODE)
    if res:
      data = json.loads(res.read())
      return data['Mode']
    return 'unknow'

  def _setStatus(self):
    res = self._post(self.STATUS, {})
    if res:
      data = json.loads(res.read())
      return res.status == 200;
    return False

  def _setServer(self, id):
    parma = {'Id': id}
    res = self._post(self.CUR_SERVER, parma)
    if res:
      data = json.loads(res.read())
      return res.status == 200;
    return False

  def _setMode(self, mode):
    parma = {'Mode': mode}
    res = self._post(self.MODE, parma)
    if res:
      data = json.loads(res.read())
      return res.status == 200;
    return False

  def action(self, query):
    args = self._parseArgs(query)
    command = args[0]
    value = args[1]
    if(command == 'enable'):
      if(self._setStatus()):
        print('Set ShadowSock ' + value + ' Succeed!')
    if(command == 'server'):
      if(self._setServer(value)):
        print('Set Server ' + args[2])
    if(command == 'mode'):
      if(self._setMode(value)):
        print('Set Server Mode: ' + value + ' Succeed!')
    return ''


  def getList(self):
    list = self._getServers()
    current = self._getCurrentServer()
    active = self._getCurrentServer()
    enable = self._getStatus()
    enableStr = 'Enable' if enable else 'Disable'
    enableOptStr = 'Disable' if enable else 'Enable'
    mode = self._getMode()
    items = []
    if list and mode:
      def setToggler():
        enableItem = {
          'title':'Toggle',
          'subtitle': 'Current: '+ enableStr,
          'arg': 'enable:'+enableOptStr,
          'icon': {'path': 'icon.png'}
        }
        if not enable:
          enableItem['icon']['path'] = 'iconb.png'
        items.append(enableItem)

      def setModes():
        for m in self.MODES:
          modeItem = {
            'title': 'Mode: '+m.title(),
            'arg': 'mode:'+m,
            'icon': {'path': 'iconb.png'}
          }
          if m == mode:
            modeItem['icon']['path'] = 'icon.png'
            modeItem['subtitle'] = 'Current Mode'
          else:
            modeItem['subtitle'] = 'Switch to ' + m
          items.append(modeItem)

      def setServers():
        for item in list:
          serverItem = {
            'title': 'Server: ' + item['Remark'],
            'arg': 'server:' +item['Id']+':'+item['Remark'],
          }
          if item['Id'] != current['Id']:
            serverItem['icon'] = {'path': 'iconb.png'}
          items.append(serverItem)
      setToggler()
      setModes()
      setServers()

    else:
      notRuning = {
        'title':'ShadowSocks is not runing',
        'subtitle': 'Please start ShadowSocks or update to new version.',
        'icon': {'path': 'iconb.png'}
      }
      items.append(notRuning)
    result = {'items': items}
    print(json.dumps(result))

