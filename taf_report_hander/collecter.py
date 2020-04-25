# coding: utf-8
import sys
import urllib.request
import urllib.parse
import os
import random
import json as js
import time
import re
from datetime import datetime
import logging
import json

logger = logging.getLogger('root')

def random_header():
    '''随机获取请求Header信息'''
    header_list = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv2.0.1)'\
            ' Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (Windows NT 6.1; rv2.0.1) '\
            'Gecko/20100101 Firefox/4.0.1',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) '\
            'Presto/2.8.131 Version/11.11',
        'Opera/9.80 (Windows NT 6.1; U; en) '\
            'Presto/2.8.131 Version/11.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) '\
            'AppleWebKit/535.11 (KHTML, like Gecko) '\
            'Chrome/17.0.963.56 Safari/535.11',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) '\
            'Gecko/20100101 Firefox/57.0'
          ]
    return random.choice(header_list)

def get_url(icao, kind, source='awc'):
    '''根据机场ICAO代号获取指定类型报文的URL'''
    if source == 'awc':
        url = 'https://aviationweather.gov/adds/' \
              'dataserver_current/httpparam?' \
              'dataSource={0}s&requestType=retrieve&format=xml' \
              '&stationString={1}&hoursBeforeNow=2' \
              '&mostRecent=true'.format(kind, icao)
    elif source == 'avt7':
        url = 'http://www.avt7.com/Home/' \
              'AirportMetarInfo?airport4Code={0}'.format(icao)
    elif source == 'nmc':
        url = f'http://aviation.nmc.cn/json_data/html/{icao}.html'
    elif source == 'caac':
        url = f'http://www.nemcaac.cn/dbinfo/app/common/airrpt/query?oneCccc={icao}&type=SA&type=SP&type=FC&type=FT&type=WA&type=WS&hour=0'

    return url

def get_web_code(url):
    '''根据url获取网页源代码'''
    req = urllib.request.Request(url)
    header = random_header()
    req.add_header('User-Agent',header)
    try:
        web_code = urllib.request.urlopen(req).read().decode('utf-8')
    except KeyboardInterrupt:
        exit()
    except:
        web_code = None
    return web_code

def parse_rpt(web_code,kind='METAR',source='awc'):
    '''从网页代码中解析出报文数据'''
    web_code = web_code.replace('\n', ' ')
    if source == 'awc':
        metar_pattern = '[A-Z]{4} \d{6}Z [0-9A-Z\s/]+'
        taf_pattern = 'TAF [A-Z]{4} \d{6}Z[0-9A-Z\s/]+'
        if kind == 'METAR':
            try:
                head_pattern = '<metar_type>[A-Z]+</metar_type>'
                head_line = re.search(head_pattern,web_code).group()
                head = re.search('[A-Z]+', head_line).group()
                rpt = head+' '+re.search(metar_pattern,web_code).group()
            except AttributeError:
                rpt = None
        elif kind == 'TAF':
            try:
                rpt = re.search(taf_pattern,web_code).group()
            except AttributeError:
                rpt = None
    elif source in ['avt7', 'caac', 'nmc']:
        metar_pattern = '(METAR|SPECI).+?='
        taf_pattern = 'TAF.+?='
        if kind == 'METAR':
            try:
                rpt = re.search(metar_pattern,web_code).group()
            except AttributeError:
                rpt = None
        elif kind == 'TAF':
            try:
                rpt = re.search(taf_pattern,web_code).group()
            except AttributeError:
                rpt = None

    return rpt

def get_single_rpt(icao,kind='METAR',source='awc'):
    url = get_url(icao, kind,source)
    web_code = get_web_code(url)
    rpt = parse_rpt(web_code,kind,source)
    return rpt

def get_rpts(icaos,kind='METAR',source='awc'):
    '''批量获取航空报文

    输入参数
    -------
    kind : `str`
        报文类型，可供选择的选项为:'METAR'和'TAF'

    返回值
    -----
    `dict` : 以ICAO码为键，以报文内容为值的字典
    '''
    rpts = {}
    total = len(icaos)
    for n,icao in enumerate(icaos):
        rpt = get_single_rpt(icao,kind=kind,source=source)
        print(rpt)
        if rpt:
            rpts[icao] = rpt
            print('{0}: ({2}/{3}) {1} finished'.format(datetime.utcnow(),
                                                      icao,n+1,total))
            logger.info(' ({1}/{2}) {0} finished'.format(icao,n+1,total))
        else:
            print('{0}: ({2}/{3}) {1} missing'.format(datetime.utcnow(),
                                                      icao,n+1,total))
            logger.info(' ({1}/{2}) {0} missing'.format(icao,n+1,total))
        time.sleep(1)
    return rpts

if __name__ == "__main__":
    icaos = [
    "ZBAA", "ZBTJ", "ZBSJ", "ZBCD", "ZBHD", "ZBDH", "ZBSN","ZBAD",
    "ZBZJ", "ZBYN", "ZBCZ", "ZBDT", "ZBLF", "ZBLL", "ZBXZ", "ZBYC",
    "ZBHH", "ZBES", "ZBAL", "ZBAR", "ZBYZ", "ZBOW", "ZBCF", "ZBDS",
    "ZBEN", "ZBER", "ZBLA", "ZBHZ", "ZBMZ", "ZBTL", "ZBUH", "ZBUC",
    "ZBUL", "ZBXH", "ZBZL", "ZYTX", "ZYAS", "ZYCY", "ZYCH", "ZYTL",
    "ZYDD", "ZYJZ", "ZYYK", "ZYCC", "ZYBA", "ZYBS", "ZYSQ", "ZYTN",
    "ZYYJ", "ZYHB", "ZYDQ", "ZYFY", "ZYHE", "ZYJX", "ZYJD", "ZYJM",
    "ZYJS", "ZYMH", "ZYMD", "ZYQQ", "ZYDU", "ZYLD", "ZSSS", "ZSPD",
    "ZSNJ", "ZSCG", "ZSSH", "ZSLG", "ZSNT", "ZSWX", "ZSXZ", "ZSYN",
    "ZSYA", "ZSOF", "ZSAQ", "ZSJH", "ZSFY", "ZSTX", "ZSHC", "ZSNB",
    "ZSJU", "ZSLQ", "ZSWZ", "ZSYW", "ZSZS", "ZSFZ", "ZSLO", "ZSQZ",
    "ZSSM", "ZSWY", "ZSAM", "ZSCN", "ZSGZ", "ZSJD", "ZSGS", "ZSSR",
    "ZSYC", "ZSJN", "ZSDY", "ZSJG", "ZSLY", "ZSQD", "ZSRZ", "ZSWF",
    "ZSWH", "ZSYT", "ZHHH", "ZHES", "ZHSN", "ZHSY", "ZHXF", "ZHYC",
    "ZHCC", "ZHLY", "ZHNY", "ZGHA", "ZGCD", "ZGHY", "ZGCJ", "ZGSY",
    "ZGLG", "ZGDY", "ZGGG", "ZGFS", "ZGHZ", "ZGOW", "ZGMX", "ZGSZ",
    "ZGZJ", "ZGSD", "ZGNN", "ZGBS", "ZGBH", "ZGKL", "ZGHC", "ZGZH",
    "ZGWZ", "ZJHK", "ZJQH", "ZJSY", "ZJYX", "ZUCK", "ZUQJ", "ZUWX",
    "ZUUU", "ZUHY", "ZUDX", "ZUDC", "ZUKD", "ZUGU", "ZUJZ", "ZULZ",
    "ZUMY", "ZUNC", "ZUZH", "ZUXC", "ZUYB", "ZPPP", "ZPBS", "ZPCW",
    "ZPDL", "ZPMS", "ZPDQ", "ZPJM", "ZPLJ", "ZPLC", "ZPNL", "ZPSM",
    "ZUTC", "ZPWS", "ZPJH", "ZPZT", "ZULS", "ZUAL", "ZUBD", "ZUNZ",
    "ZURK", "ZLXY", "ZLHZ", "ZLYA", "ZLYL", "ZLLL", "ZLDH", "ZLXH",
    "ZLJQ", "ZLJC", "ZLLN", "ZLQY", "ZLTS", "ZLZY", "ZLIC", "ZLGY",
    "ZLZW", "ZWWW", "ZWAK", "ZWAT", "ZWBL", "ZWKN", "ZWFY", "ZWHM",
    "ZWTN", "ZWSH", "ZWKM", "ZWKC", "ZWKL", "ZWCM", "ZWSC", "ZWHZ",
    "ZWTC", "ZWTP", "ZWNL", "ZWYN", "VHHH", "VMMC", "ZUGY", "ZUAS",
    "ZUBJ", "ZUKJ", "ZULB", "ZUNP", "ZUPS", "ZUTR", "ZUYI", "ZUMT",
    "ZUZY", "ZLXN", "ZLDL", "ZLGM", "ZLGL", "ZLHX", "ZLYS", "ZUGH",
    "RCSS", "RCKH", "RCTP", "RCYU", "ZHXY", "ZUWS", "ZUBZ", "ZUGZ",
    "RCMQ", "ZGYY", "ZWRQ", "ZWTS", "RCNN", "RCKU", "RCFN", "RCQC",
    "RCBS"
    ]
    # for i in range(len(icaos)):
    #     icao = icaos[i]
    #     rpt = get_single_rpt(icao,'TAF','avt7')
    #     print(rpt)
    rpts = get_rpts(icaos,'TAF','avt7')
    with open("TAF.json", "w") as f:
        json.dump(rpts, f)
        print("加载入文件完成...")
    # rpt = get_single_rpt('ZBSN','METAR','nmc')
    # print(rpt)