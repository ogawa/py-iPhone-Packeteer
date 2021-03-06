#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import mechanize
import re
import time
import datetime

class iPhonePacketeer:
  def __init__(self, username='', password=''):
    br = mechanize.Browser()
    br.set_handle_refresh(True)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_0 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5A345 Safari/525.20')]
    self.br = br
    if username:
      self.__username = username
    if password:
      self.__password = password
    self.__html = None

  def __request(self):
    br = self.br

    # login
    br.open('https://my.softbank.jp/msb/d/top')
    br.select_form(nr=0)
    br['msn'] = self.__username
    br['password'] = self.__password
    br.submit()

    # jump to mainmenu
    br.open('https://my.softbank.jp/msb/d/webLink/doSend/WCO010000')

    # jump to bill_before_fixed
    br.open('https://bl11.my.softbank.jp/wco/billBeforeFixed/WCO020')

    self.__html = br.response().read().decode('cp932')

  def html(self):
    if self.__html == None:
      self.__request()
    return self.__html

  def fee(self, prev=0):
    if self.__html == None:
      self.__request()
    if prev == 0:
      html = self.__html.split(u'>前月分')[0]
    else:
      html = self.__html.split(u'>前月分')[1]
    fee_total = 0
    r = re.compile(u'通信料.+?([0-9,]+)円')
    for fee in r.findall(html):
      fee_total += int(re.sub(',', '', fee))
    return fee_total

  def packets(self, prev=0):
    fee = self.fee(prev=prev)
    return fee / 0.08

  def bytes(self, prev=0):
    fee = self.fee(prev=prev)
    return (fee / 0.08) * 128

  def ts_begin(self, prev=0):
    if self.__html == None:
      self.__request()
    m = re.search(u'当月分.+?（([A-Za-z 0-9:]+)～', self.__html)
    struct_time = time.strptime(m.group(1), "%a %b %d %H:%M:%S %Z %Y")
    return datetime.datetime(*struct_time[:6])

  def ts_end(self):
    if self.__html == None:
      self.__request()
    m = re.search(u'当月分.+?([A-Za-z 0-9:]+)）', self.__html)
    struct_time = time.strptime(m.group(1), "%a %b %d %H:%M:%S %Z %Y")
    return datetime.datetime(*struct_time[:6])

  def timestamp(self):
    return self.ts_end()

def main():
  config = yaml.safe_load(
    open(
      os.path.join(os.path.dirname(__file__), 'iphone_packeteer.yaml')
      ).read().decode('utf-8')
    )
  packeteer = iPhonePacketeer(
    username=config['username'],
    password=config['password']
    )
  print packeteer.ts_begin().strftime("%Y-%m-%d"), packeteer.ts_end().strftime("%Y-%m-%d"), packeteer.fee()

if __name__ == '__main__':
  main()
