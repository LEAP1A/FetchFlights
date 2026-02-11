import random
from FlightRadar24 import FlightRadar24API
import time
import os
import datetime
# 当前进度: 能够完整地获取指定机场一整天的计划航班并存入txt。
# 下一步: 添加判断脚本运行时间是0点前还是0点后 从而决定要拿哪一天的数据; 定义宏方便修改数据; 添加写入csv为后续筛选做准备; 航班的筛选需要新开一个py文件

def main():
    fr_api = FlightRadar24API()  # 初始化 FR24 接口

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    day_after_tomorrow = today + datetime.timedelta(days=2)

    # Convert dates to string format for easy comparison
    target_date_str = tomorrow.strftime("%Y-%m-%d")
    stop_date_str = day_after_tomorrow.strftime("%Y-%m-%d") # 停止获取的日期,可更改 - 0点前跑脚本为day_after_tomorrow, 0点后跑脚本为tomorrow_date

    # 获取机场对象 (Xi'an Xianyang International Airport)
    airport_code = "ZLXY"
    txtFileName = f"{airport_code}_{target_date_str}_arrivals.txt"

    # schedule - arrivals - page: total = 总页数 current = 当前页数
    if os.path.exists(txtFileName):
        print(f"File '{txtFileName}' already exists.")
    else:
        print("Fetching Data From API...")
        fullScheduleData = fr_api.get_airport_details(airport_code, page=1)['airport']['pluginData']['schedule']
        totalPages = fullScheduleData['arrivals']['page']['total']  # 总页数
        print(f"There are totally {totalPages} pages of schedule flights")
        
        arrivalsList = fullScheduleData['arrivals']['data']
        
        # Write Header
        with open(txtFileName, 'w', encoding='utf-8') as f:
            header = f"{'Flight':<10} | {'Airline':<40} | {'Arrival Time':<20} | {'Origin':<8} | {'Model':<8} | {'Reg'}\n"
            f.write(header)
            f.write("-" * 105 + "\n")
        # Write the first page
        write_onePage_to_file(arrivalsList, txtFileName, stop_date_str)
        randNum = random.uniform(3, 5)
        print(f"Page 1 done. Waiting for {randNum:.2f} seconds before fetching the next page...")
        time.sleep(randNum)
        # Iterate the remaining pages and write to file
        for pageNum in range(2, totalPages+1):
            print(f"Fetching page {pageNum}...")
            fullScheduleData = fr_api.get_airport_details(airport_code, page=pageNum)['airport']['pluginData']['schedule']
            arrivalsList = fullScheduleData['arrivals']['data']
            if not (write_onePage_to_file(arrivalsList, txtFileName, stop_date_str)):
                break
            if pageNum < totalPages:
                randNum = random.uniform(2, 5)
                print(f"Page {pageNum} done. Waiting for {randNum:.2f} seconds before fetching the next page...")
                time.sleep(randNum)
            
        print("All Done!")
            
def write_onePage_to_file(arrivalsList, txtFileName, stop_date_str):
    with open(txtFileName, 'a', encoding='utf-8') as f:
        for item in arrivalsList:
            # Get the main flight object safely
            flight = item.get('flight') or {}

            # 1. Flight Number / Callsign
            # Try callsign first, then default number, else "N/A"
            identification = flight.get('identification') or {}
            flight_num = identification.get('callsign') or identification.get('number', {}).get('default') or "N/A"

            # 2. Airline Name
            airline = flight.get('airline') or {}
            airline_name = airline.get('name') or "Unknown Airline"

            # 3. Scheduled Arrival Time
            time_info = flight.get('time') or {}
            scheduled = time_info.get('scheduled') or {}
            arrival_ts = scheduled.get('arrival')

            if arrival_ts:
                # Convert timestamp to readable string
                arrival_time_obj = datetime.datetime.fromtimestamp(arrival_ts)
                arrival_date_str = arrival_time_obj.strftime('%Y-%m-%d')
                arrival_fulltime_str = arrival_time_obj.strftime('%Y-%m-%d %H:%M')
                if arrival_date_str >= stop_date_str: # 超过一天的日期就不拿了
                    return False
            else:
                arrival_fulltime_str = "N/A"

            # 4. Origin Airport Code
            airport = flight.get('airport') or {}
            origin = airport.get('origin') or {}
            origin_code = "N/A"
            if origin.get('code'):
                origin_code = origin['code'].get('iata') or "N/A"

            # 5. Aircraft Information
            aircraft = flight.get('aircraft') or {}
            
            # Get model code (e.g., B738)
            model_code = "N/A"
            if aircraft.get('model'):
                model_code = aircraft['model'].get('code') or "N/A"
            
            # Get registration (e.g., B-1234)
            registration = aircraft.get('registration') or "N/A"

            # 6. Write formatted line to file
            # Slice airline_name[:25] to prevent long names from breaking the table alignment
            line = f"{flight_num:<10} | {airline_name[:40]:<40} | {arrival_fulltime_str:<20} | {origin_code:<8} | {model_code:<8} | {registration}\n"
            f.write(line)
    return True

if __name__ == "__main__":
    main()

 

