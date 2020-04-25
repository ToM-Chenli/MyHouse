# # coding: utf-8
'''
该代码片段主要爬虫飞常准网站的数据，
网址为：
https://data.variflight.com/analytics/Real-timeOperationByCN
记录日期：2020年4月21日
'''
import requests
from bs4 import BeautifulSoup
import json
import csv
import time


def get_count():
    url = 'https://data.variflight.com/analytics/Otpapi/delayCount'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    text = soup.text
    dict = json.loads(text)
    delay_flight_count = dict['data']['delay_flight_count']
    cancel_count = dict['data']['cancel_count']
    return delay_flight_count, cancel_count


def get_airport():
    url = 'https://data.variflight.com/analytics/Otpapi/todayMost'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    text = soup.text
    dict = json.loads(text)
    # 目的机场
    delayInMostAirport = dict['data']['decan_airport_in_max']['airport_name']
    delayInMostCancelNum = dict['data']['decan_airport_in_max']['delay_cancel']
    # 起飞机场
    delayOutMostAirport = dict['data']['decan_airport_out_max']['airport_name']
    delayOutMostCancelNum = dict['data']['decan_airport_out_max']['delay_cancel']
    return delayInMostAirport, delayInMostCancelNum, delayOutMostAirport, delayOutMostCancelNum


def get_delayairport():
    url = 'https://data.variflight.com/analytics/Otpapi/airportDelay'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    text = soup.text
    dict = json.loads(text)
    delayairport_array = []
    airport_array = dict['data']
    for i in range(len(airport_array)):
        delayairport = airport_array[i]['airport_name']
        delayairport_array.append(delayairport)
    return delayairport_array


def get_specialairport():
    url = 'https://data.variflight.com/analytics/Otpapi/airportSpecial'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    text = soup.text
    dict = json.loads(text)
    special_airport = []
    condition = []
    airport_array = dict['data']
    for j in range(len(airport_array)):
        special_airport.append(airport_array[j]['airport_name'])
        condition.append(airport_array[j]['weather'])
    return special_airport, condition


if __name__ == "__main__":
    csvfile = open('data.csv', 'w', encoding='gbk')
    writer = csv.writer(csvfile)
    writer.writerow(["decanTime", "cancelNum", "delayNum", "delayAirport", "delayOutMostAirport",
                     "delayOutMostCancelNum", "delayInMostAirport", "delayInMostCancelNum",
                     "specialAirport_1", "condition_1", "specialAirport_2", "condition_2",
                     "specialAirport_3", "condition_3"])
    data = []
    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    delay_flight_count, cancel_count = get_count()
    delayInMostAirport, delayInMostCancelNum, delayOutMostAirport, delayOutMostCancelNum = get_airport()
    delayairport_array = get_delayairport()
    special_airport, condition = get_specialairport()

    data.append(nowtime)
    data.append(cancel_count)
    data.append(delay_flight_count)
    data.append(delayairport_array)
    data.append(delayOutMostAirport)
    data.append(delayOutMostCancelNum)
    data.append(delayInMostAirport)
    data.append(delayInMostCancelNum)
    for i in range(len(special_airport)):
        data.append(special_airport[i])
        data.append(condition[i])
        if i == 2:
            break
    writer.writerow(data)
    print(data)
    csvfile.close()
