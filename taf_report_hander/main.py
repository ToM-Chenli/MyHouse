'''
该文件主要是解析爬取到TAF报文，
为航空简报做数据支撑，解析.json数据来进行解析
'''
import numpy as np
import json
import re
import xlrd
import csv
weather_symbol = ['-','+',
                  'TS',
                   'RA','SN',
                  'DU','SA','HZ',
                  ]
weather_translate = ['小','大',
                    '雷暴',
                    '雨','雪',
                    '大范围浮尘','沙','霾',
                    ]

def json_loader():
    json_file  = open('TAF.json','r')
    csv_file = open("result.csv",'w',newline='')
    csv_writer = csv.writer(csv_file,dialect = 'excel')
    title = ['weatherTime','weatherAirportName','weatherAirportDetail']
    csv_writer.writerow(title)
    data  = json.load(json_file)
    airports = list(data.keys())
    airport_icao, icao_transform_name = icao_loader()
    for i in range(len(airports)):
        airport = airports[i]
        report = data[airport]
        report = standard_report(report)
        if (report == None):
            continue
        else:
            # 找到观测的时间和日期,并且转化为北京时间
            r_for_time = re.compile(r'\d+Z')
            s1 = r_for_time.search(report)
            orig_time = s1.group(0)
            real_time = time_hander(orig_time)  # 这个是需要返回的信息正确的时间

            # 找到风向风速
            r_for_wind = re.compile(r'V*R*B*\d+G*\d+KT|V*R*B*\d+G*\d+MPS|V*R*B*\d+G*\d+KMH')
            s_for_wind = r_for_wind.search(report)
            if s_for_wind == None:
                direction, wind, gust = wind_hander('00000')
                begin_number = report.find('00000')
                report = report[begin_number+5:]
            else:
                direction, wind, gust = wind_hander(s_for_wind.group(0))
                begin_number = report.find(s_for_wind.group(0))
                report = report[begin_number + len(s_for_wind.group(0)):]

            # 整个的天气情况包括：能见度、云层高度、降水降雨情况
            r_for_weather = re.compile(r'CAVOK')
            s_for_weather = r_for_weather.search(report)
            if s_for_weather == None:
                # 可见度处理部分
                if '9999' in report:
                    visibility = '10000'
                    report = report.replace('9999', '')
                    report = report.strip()
                elif 'P6SM' in report:
                    visibility = '10000'
                    report = report.replace('P6SM', '')
                    report = report.strip()
                elif '0000' in report:
                    visibility = '50'
                    report = report.replace('0000', '')
                    report = report.strip()
                else:
                    str_visibility = report.split()[0]
                    visibility = str_visibility
                    report = report.replace(visibility, '')
                    report = report.strip()
            else:
                visibility = '10000'
                report = report.replace('CAVOK', '')
                report = report.strip()

            weather_for_str, weather_for_translate = weather_hander(report)
            weather_detail = ''
            wind = int(wind)
            visibility = int(visibility)
            if(wind >= 10 ):
                wind = '风速' + str(wind) + 'm/s,'
                weather_detail = weather_detail + wind
            if(visibility <= 2000 ):
                visibility = '能见度' + str(visibility) + 'm,'
                weather_detail = weather_detail + visibility
            if(weather_for_translate != ''):
                weather_detail = weather_detail + weather_for_translate
            if(airport in airport_icao and weather_detail != ''):
                weather_data = []
                weather_data.append(real_time)
                weather_data.append(icao_transform_name[airport])
                weather_data.append(weather_detail)
                csv_writer.writerow(weather_data)
    json_file.close()
    csv_file.close()

#首先对TAF进行规范化，去除更新的报文（无任何价值）和趋势报文(处理过于繁琐，目前阶段用不到）
def standard_report(report):
    match_str1 = 'BECMG'
    match_str2 = 'TEMPO'
    match_str3 = 'AMD'
    result = re.search(match_str1,report)
    if (result != None):
        span = re.search(match_str1,report).span()
        report = report[:span[0]]
        return report
    else:
        result = re.search(match_str2,report)
        if(result != None):
            span = re.search(match_str2, report).span()
            report = report[:span[0]]
            return report
    if re.search(match_str3,report) != None:
        return None
    return report

def icao_loader():
    json_file = open('ICAO.json', 'r')
    data = json.load(json_file)
    airports = list(data.keys())
    json_file.close()
    return  airports,data


#时间处理函数
def time_hander(time_str):
    day = int(time_str[:2])
    hour = int(time_str[2:4])
    min = int(time_str[4:6])
    hour = hour + 8
    if hour > 23:
        hour = hour - 24
    real_time = str(hour) + ':' + str(min)
    return real_time

#风向风速的处理函数
def wind_hander(str_wind):
    if str_wind == '00000':
        direction = 'unidentified'
        wind_speed = '0'
        gust_speed = '0'
        return direction,wind_speed,gust_speed
    else:
        if 'VRB' in str_wind:
            direction = 'unidentified'
        else:
            direction = str(int(str_wind[0:3]))
        str_wind = str_wind[3:]
        r_for_wind_speed = re.compile(r'\d+')
        wind_speed = str(int(r_for_wind_speed.search(str_wind).group(0)))
        wind_speed_len = len(r_for_wind_speed.search(str_wind).group(0))
        str_wind = str_wind[wind_speed_len:]
        if 'G' in str_wind:
            r_for_gust_speed = re.compile(r'\d+')
            gust_speed = str(int(r_for_gust_speed.search(str_wind).group(0)))
            gust_speed_len = len(r_for_gust_speed.search(str_wind).group(0))
            str_wind = str_wind[gust_speed_len+1:]
        else:
            gust_speed = 0

        unit = str_wind #MPS m/s KMH km/h KT 节
        wind_speed = str(wind_speed)
        gust_speed = str(gust_speed)
        if unit == 'KT':
            wind_speed = str(int(int(wind_speed) * 1852 / 3600))
            gust_speed = str(int(int(gust_speed) * 1852 / 3600))
        elif unit == 'KMH':
            wind_speed = str(int(int(wind_speed) * 1000 / 3600))
            gust_speed = str(int(int(gust_speed) * 1000 / 3600))
    return direction,wind_speed,gust_speed

#天气处理函数
def weather_hander(weather_str):
    weather_for_str = ''
    weather_for_translate = ''
    for i in range(len(weather_symbol)):
        symbol_for_str = weather_symbol[i]
        if symbol_for_str in weather_str and 'OVC' not in weather_str:
            weather_for_str = weather_for_str + symbol_for_str
            weather_for_translate = weather_for_translate + " " + weather_translate[i]
    return weather_for_str,weather_for_translate
if __name__ == "__main__":
    json_loader()
