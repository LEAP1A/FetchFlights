import csv
import re 
import datetime

def run_filtering(airport_code, target_date_str, target_model_lst, start_time_str):
    
    # File Names
    csvFileName = f"{airport_code}_{target_date_str}_arrivals.csv"  
    outputFileName = f"{airport_code}_{target_date_str}_selected_arrivals.md" # Changed to .md

    count = 0
    try:
        with open(csvFileName, 'r', encoding='utf-8') as f_in, \
             open(outputFileName, 'w', encoding='utf-8') as f_out:
            
            reader = csv.reader(f_in)
            
            # 1. Write Markdown Title and Table Header 
            f_out.write(f"# {airport_code} - {target_date_str} Selected Flights from {start_time_str}\n\n")
            f_out.write(f'<span style="color: orange"><b>Special Livery=Orange</b></span>; ')
            f_out.write(f'<span style="color: #39FF14"><b>Wide-body=Bright Green</b></span>; ')
            f_out.write(f'<span style="color: #4682B4"><b>Other Selected Models=Dark Blue</b></span>; ')
            f_out.write(f'<span style="color: red"><b>Non-Chinese Reg=Red</b></span>\n\n')
            
            f_out.write("| Flight | Airline | Arrival Time | Model | Reg | Origin |\n")
            f_out.write("|---|---|---|---|---|---|\n") # Separator line

            for row in reader:
                # Skip empty lines
                if not row:
                    continue
                
                # Unpack row
                flight_num = row[0]
                airline_name = row[1]
                arrival_time = row[2]
                origin_code = row[3]
                model_code = row[4]
                registration = row[5]

                # Initialize highlight variables (default is normal text)
                disp_airline = airline_name
                disp_model = model_code
                disp_reg = registration
                
                is_selected = False

                # --- Filter 1: Airline check (Orange + Bold) ---
                if "(" in airline_name:
                    is_selected = True
                    # 橙色 + 加粗
                    disp_airline = f'<span style="color: orange"><b>{airline_name}</b></span>'

                # --- Filter 2: Model check (Blue + Bold) ---
                if model_code in target_model_lst:
                    is_selected = True
                    
                    if model_code in [ # 宽体 = 亮绿色 + 加粗 
                        "A330", "A332", "A333", "A339", "A359", "B763", "B772", "B77L", "B77W", "B788", "B789", "B744", "IL76", 
                        "330", "332", "333", "359", "76F", "77F", "77L", "773", "77W", "777", "788", "789", "744"]:
                        disp_model = f'<span style="color: #39FF14"><b>{model_code}</b></span>'
                    else: # 其他 = 薄荷青 + 加粗 
                        disp_model = f'<span style="color: #4682B4"><b>{model_code}</b></span>'

                # --- Filter 3: Registration check (Red + Bold) ---
                if registration != "N/A" and airport_code.startswith("Z"): # 只针对中国机场进行非中国注册号的高亮
                    if not re.match(r"^B-\d", registration):
                        is_selected = True
                        # 红色 + 加粗
                        disp_reg = f'<span style="color: red"><b>{registration}</b></span>'

                # --- Write row if selected ---
                # 选择几点之后的航班
                if is_selected and arrival_time >= f"{target_date_str} {start_time_str}":
                    # Construct Markdown table row using pipes |
                    line = f"| {flight_num} | {disp_airline} | {arrival_time} | {disp_model} | {disp_reg} | {origin_code} |\n"
                    f_out.write(line)
                    count += 1

        print(f"Done! Found {count} flights. Saved to {outputFileName}")
        print("Tip: Open the .md file in VS Code and press 'Ctrl + Shift + V' to see the pretty table.")

    except FileNotFoundError:
        print(f"Error: The file '{csvFileName}' was not found. Please check the filename.")

if __name__ == "__main__": 
    print("单独调试 filter_flights.py\n")
    TARGET_MODELS = [  # Target Aircraft Models 仅在单独调试时使用
        "A19N", "A330", "A332", "A333","A339", "A359", "B733", "B734", "B752", "B763", "B772", "B77L", "B77W", "B788", "B789", "B744", "AJ27", "C919", "IL76", 
        "330", "332", "333", "359", "739", "73F", "75F", "76F", "77F", "77L", "773", "77W", "777", "788", "789", "744", "C09", "909", "919"
    ]
    run_filtering("ZLXY", datetime.date.today().strftime("%Y-%m-%d"), TARGET_MODELS, "08:00") # 指定时间后再调试