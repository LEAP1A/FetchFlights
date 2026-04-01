import csv
import re 
import json
import requests
import time
import random

def run_filtering(airport_code, target_date_obj, target_model_lst, start_time_str):
    
    target_date_str = target_date_obj.strftime("%Y-%m-%d")
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
            f_out.write(f'<span style="color: orange"><b>Special Livery=Orange </b></span>')
            f_out.write(f'<span style="color: #39FF14"><b> | Wide-body=Bright Green </b></span>')
            f_out.write(f'<span style="color: #4682B4"><b> | Other Selected Models=Dark Blue </b></span>')
            f_out.write(f'<span style="color: red"><b> | Non-Chinese Reg=Red</b></span>\n\n') if airport_code.startswith("Z") else f_out.write("\n\n")
            
            f_out.write("| Flight | Airline | Arrival Time | Model | Reg | Origin |\n")
            f_out.write("|---|---|---|---|---|---|\n")

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
                model_full = row[6]

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
                        "330", "332", "333", "359", "76F", "77X", "77F", "77L", "773", "77W", "777", "788", "789", "744"]:
                        disp_model = f'<span style="color: #39FF14"><b>{model_code}</b></span>'
                    else: # 其他 = 薄荷青 + 加粗 
                        disp_model = f'<span style="color: #4682B4"><b>{model_code}</b></span>'
                # Select Cargo
                if "f" in model_full.lower() or "cargo" in airline_name.lower() or model_code in ["73F","75F", "76F", "77F", "77X", "74Y", "IL76"]:
                    is_selected = True
                    disp_model = f'<span style="color: #4682B4"><b>{model_code}(Cargo)</b></span>'

                # --- Filter 3: Registration check (Red + Bold) ---
                if registration != "N/A" and airport_code.startswith("Z"): # 在中国机场排除中国大陆注册号
                    if not re.match(r"^B-\d", registration) or len(registration) > 6: # 排除中国注册号 允许港台注册号
                        is_selected = True
                        # 红色 + 加粗
                        disp_reg = f'<span style="color: red"><b>{registration}</b></span>'
                        
                if airport_code == "VHHH": # HKG
                    if airline_name == "Cathay Pacific" and "(" not in airline_name: # HKG跳过国泰普通涂装
                        continue
                    if (registration != "N/A" and not re.match(r"^B-", registration)) or (len(registration) > 6): # 排除港澳注册号和中国注册号 但允许台湾注册号
                        is_selected = True
                        # 红色 + 加粗
                        disp_reg = f'<span style="color: red"><b>{registration}</b></span>'
                        
                if registration != "N/A" and airport_code == "VMMC": # MFM
                    if (not re.match(r"^B-", registration)) or (len(registration) > 6): # 排除港澳注册号和中国注册号 但允许台湾注册号
                        is_selected = True
                        # 红色 + 加粗
                        disp_reg = f'<span style="color: red"><b>{registration}</b></span>'

                # --- Write row if selected ---
                # 选择几点之后的航班
                if is_selected and arrival_time >= f"{target_date_str[5:]} {start_time_str}":
                    # Construct Markdown table row using pipes |
                    line = f"| {flight_num} | {disp_airline} | {arrival_time} | {disp_model} | {disp_reg} | {origin_code} |\n"
                    f_out.write(line)
                    count += 1

        print(f"Done! Found {count} flights. Saved to {outputFileName}")
        print("Tip: Open the .md file in VS Code and press 'Ctrl + Shift + V' to see the pretty table.")

    except FileNotFoundError:
        print(f"Error: The file '{csvFileName}' was not found. Please check the filename.")

# -------------------------- For MiniProgram -------------------------------
# 在HKG的筛选逻辑与输出为.md的有所不同，将保留HKG的宽体
def run_filterToJson(airport_code, target_date_obj, target_model_lst):
    target_date_str = target_date_obj.strftime("%Y-%m-%d")
    # 文件名替换为 .json
    csvFileName = f"{airport_code}_{target_date_str}_arrivals.csv"  
    outputFileName = f"{airport_code}_{target_date_str}_selected_arrivals.json"
    
    wide_body_list = [ 
        # 宽体
        "A124", "A306", "A19N", "A332", "A333", "A339", "A343", "A345", "A346", "A359", "A35K", "A388",
        "B742", "B744", "B748", "B762", "B763", "B764", "B772", "B77L", "B773", "B77W", "B788", "B789", "B78X",
        "IL62", "IL76", "IL96", "MD11",  "IL6", "IL7", "I93",
        # IATA
        "M1F", "330", "332", "333", "339", "343", "346", "359", "351", "388",
        "742", "744", "74H", "74N", "74X", "74Y", "763", "76W", "76X", "76Y", "772", "773", "77X", "77F", "77L", "77W", "788", "789", "781"
    ]
    cargo_model_dic = {"73F":"732F", "73Y":"733F", "73P":"B734F", "73U":"738F", "75F":"757F", "76X": "762F", "76Y":"763F", "77X":"772F", "B77L": "772F", "74N":"748F", "74X":"742F", "74Y":"744F", "ABY":"306F", "33X":"332F", "33Y":"333F", "IL7":"IL76", "IL62":"IL62", "IL6": "IL62", "IL96": "IL96", "I93": "IL96", "MD11":"MD11F", "M1F":"MD11F"}

    selected_flights = [] # 用于收集最终符合条件的航班字典

    try:
        with open(csvFileName, 'r', encoding='utf-8') as f_in:
            reader = csv.reader(f_in)
            
            for row in reader:
                # 跳过空行
                if not row:
                    continue
                
                # 解包 CSV 行
                flight_num = row[0]
                airline_name = row[1]
                arrival_time = row[2]
                origin_code = row[3]
                model_code = row[4]
                registration = row[5]
                model_full = row[6]
                status = row[7]

                is_selected = False
                
                # 构建基础数据字典，新增状态标识（默认全为 False）
                flight_data = {
                    "flightNo": flight_num,
                    "airline": airline_name,
                    "time": arrival_time,
                    "origin": origin_code,
                    "type": model_code,
                    "reg": registration,
                    "isSpecial": False,    # 是否彩绘/特装
                    "isWideBody": False,   # 是否宽体机
                    "isCargo": False,      # 是否货机
                    "isForeign": False,    # 是否外籍/特殊注册号
                    "title": '',
                    "urlImage": "",
                    "imageCreator": "",
                    "status": "Scheduled"
                }

                # --- 过滤器 1: 彩绘机检查 ---
                if "(" in airline_name:
                    is_selected = True
                    flight_data["isSpecial"] = True
                    flight_data["title"] = airline_name.split("(")[1].split(")")[0].strip()

                # --- 过滤器 2: 目标机型与宽体机检查 ---
                if model_code in target_model_lst:
                    is_selected = True
                    if model_code in wide_body_list:
                        flight_data["isWideBody"] = True
                    if flight_data["title"] == '':
                        flight_data["title"] = f"{airline_name} {model_code}"
                            
                # --- 过滤器 3: 货机检查 ---
                if "f" in model_full.lower() or "cargo" in airline_name.lower() or model_code in cargo_model_dic:
                    is_selected = True
                    flight_data["isCargo"] = True
                    if flight_data["title"] == '':
                            flight_data["title"] = f"{airline_name} {model_code}"
                    if model_code in cargo_model_dic:
                        flight_data["type"] = cargo_model_dic[model_code] # 将货机型号替换为更具体的型号
                        flight_data["title"] = f"{airline_name} {flight_data['type']}"

                # --- 过滤器 4: 注册号检查 (外籍/稀有) ---
                if registration != "N/A":
                    if airport_code.startswith("Z"): # 中国大陆机场
                        if not re.match(r"^B-\d", registration) or len(registration) > 6: # 排除中国大陆注册号 允许所有境外注册号
                            is_selected = True
                            flight_data["isForeign"] = True
                            if flight_data["title"] == '':
                                flight_data["title"] = f"{airline_name} {model_code}"
                            
                    elif airport_code == "VHHH": # HKG
                        # if airline_name == "Cathay Pacific" and "(" not in airline_name: # 暂时保留HKG的普通涂装国泰宽体
                        #     continue
                        if (not re.match(r"^B-", registration)) or (len(registration) > 6): # 在HKG/MFM需要再排除港澳注册号，只保留台湾和其他国家注册号
                            is_selected = True
                            flight_data["isForeign"] = True
                            if flight_data["title"] == '':
                                flight_data["title"] = f"{airline_name} {model_code}"
                            
                    elif airport_code == "VMMC": # MFM
                        if (not re.match(r"^B-", registration)) or (len(registration) > 6): # 在HKG/MFM需要再排除港澳注册号，只保留台湾和其他国家注册号
                            is_selected = True
                            flight_data["isForeign"] = True
                            if flight_data["title"] == '':
                                flight_data["title"] = f"{airline_name} {model_code}"
                                
                if status=='True':
                    flight_data["status"] = "Enroute"
            
                # --- 时间验证与追加 ---
                # 只有被选中，且时间晚于目标时间的航班才会被加入列表
                if is_selected:
                    if registration != "N/A":
                        print(f"Fetching {registration} image...")
                        img_url, photographer = get_plane_image(registration)
                        flight_data["urlImage"] = img_url
                        flight_data["imageCreator"] = photographer
                    selected_flights.append(flight_data)

        # 统一将 Python 列表转为 JSON 格式并写入文件
        with open(outputFileName, 'w', encoding='utf-8') as f_out:
            # indent=2 使 JSON 具有良好的缩进可读性，ensure_ascii=False 保证中文字符不乱码
            json.dump(selected_flights, f_out, indent=2, ensure_ascii=False)

        print(f"Done! Found {len(selected_flights)} flights. Saved to {outputFileName}")

    except FileNotFoundError:
        print(f"Error: The file '{csvFileName}' was not found. Please check the filename.")
        
def get_plane_image(reg):
    if not reg or reg == "N/A":
        return ""
    
    url = f"https://api.planespotters.net/pub/photos/reg/{reg}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        randNum = random.uniform(1, 5)
        time.sleep( 1 / randNum) 
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("photos") and len(data["photos"]) > 0:
                photo_info = data["photos"][0]
                img_url = photo_info["thumbnail_large"]["src"]
                photographer = photo_info.get("photographer", "Unknown") # 拿到摄影师名字
                return img_url, photographer
    except Exception as e:
        print(f"获取 {reg} 图片失败: {e}")
        
    return "", ""