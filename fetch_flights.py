import random
from FlightRadar24 import FlightRadar24API
import time
import os
import datetime
import csv  

def run_fetching(airport_code, target_date_obj):
    # 初始化
    fr_api = FlightRadar24API()  # 初始化 FR24 接口
    
    stop_date_obj = target_date_obj + datetime.timedelta(days=1)
    target_date_str = target_date_obj.strftime("%Y-%m-%d")
    stop_date_str = stop_date_obj.strftime("%Y-%m-%d")
    
    csvFileName = f"{airport_code}_{target_date_str}_arrivals.csv"

    # schedule - arrivals - page: total = 总页数 current = 当前页数
    if os.path.exists(csvFileName):
        print(f"File '{csvFileName}' already exists.")
    else:
        print(f"Deleting old files from {airport_code}...")
        [os.remove(f) for f in os.listdir('.') if f.startswith(airport_code) and f.endswith(('arrivals.csv', 'arrivals.md'))] # 删除之前日期的文件
        print("Fetching Data From API...")
        fullScheduleData = fr_api.get_airport_details(airport_code, page=1)['airport']['pluginData']['schedule']
        totalPages = fullScheduleData['arrivals']['page']['total']  # 总页数
        print(f"There are totally {totalPages} pages of schedule flights")
        
        arrivalsList = fullScheduleData['arrivals']['data']
        
        # Write the first page
        write_onePage_to_file(arrivalsList, csvFileName, stop_date_str)
        randNum = random.uniform(3, 5)
        print(f"Page 1 done. Waiting for {randNum:.2f} seconds before fetching the next page...")
        time.sleep(randNum)
        # Iterate the remaining pages and write to file
        for pageNum in range(2, totalPages+1):
            print(f"Fetching page {pageNum}...")
            fullScheduleData = fr_api.get_airport_details(airport_code, page=pageNum)['airport']['pluginData']['schedule']
            arrivalsList = fullScheduleData['arrivals']['data']
            if not (write_onePage_to_file(arrivalsList, csvFileName, stop_date_str)): # stop once encountered the next day data (which means all target date data has been fetched)
                break
            if pageNum < totalPages:
                randNum = random.uniform(2, 5)
                print(f"Page {pageNum} done. Waiting for {randNum:.2f} seconds before fetching the next page...")
                time.sleep(randNum)
            
        print("All Done!")
            
def write_onePage_to_file(arrivalsList, csvFileName, stop_date_str):
    with open(csvFileName, 'a', encoding='utf-8', newline='') as f_csv:
        
        writer = csv.writer(f_csv)

        for item in arrivalsList:
            # Get the main flight object safely
            flight = item.get('flight') or {}

            # 1. Flight Number / Callsign
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
                if arrival_date_str >= stop_date_str: 
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
            
            # Get model code
            model_code = "N/A"
            if aircraft.get('model'):
                model_code = aircraft['model'].get('code') or "N/A"
            
            # Get registration
            registration = aircraft.get('registration') or "N/A"

            # Write list row to CSV file (No header needed as per request)
            writer.writerow([flight_num, airline_name, arrival_fulltime_str, origin_code, model_code, registration])
            
    return True

if __name__ == "__main__": # 调试时解开注释并指定抓取日期
    print("单独调试 fetch_flights.py\n")
    run_fetching("ZLXY", datetime.date.today()) 

 

