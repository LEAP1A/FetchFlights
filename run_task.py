import datetime
import fetch_flights as fetch  # fetch_flights.py
import filter_flights as filter  # filter_flights.py

# ================= CONFIGURATION =================

# Target Airport ICAO
AIRPORT_CODE = "VMMC" 

TARGET_MODELS_CONFIG = [ #包括窄体
    # 窄体
    "A19N", "B733", "B734", "B735", "B736", "B752", "AJ27", "C919","C09", "909", "919", 
    # 宽体
    "A124", "A306", "A19N", "A332", "A333", "A339", "A343", "A345", "A346", "A359", "A35K", "A388",
    "B742", "B744", "B748", "B762", "B763", "B764", "B772", "B77L", "B773", "B77W", "B788", "B789", "B78X",
    "IL62", "IL76", "IL96", "MD11",  "IL6", "IL7", "I93",
    # IATA
    "M1F", "330", "332", "333", "339", "343", "346", "359", "351", "388",
    "73F", "73Y", "73P", "742", "744", "74H", "74N", "74X", "74Y", "752", "75F", "763", "76W", "76X", "76Y", "772", "773", "77X", "77F", "77L", "77W", "788", "789", "781"
]

WRITING_FOR_MINIPROGRAM = 1 # 1 = json; 0 = md

FILTER_START_TIME = "04:00" # 只在写入到.md下生效, json文件默认从00:00开始筛选

# ======================================================================
def main():
    
    # --- Calculate the target day ---
    # 逻辑: 中午12点后，目标日期是明天；否则是今天。
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    # -------------------正式运行前修改------------------------
    target_date_obj = tomorrow # FOR DEBUGGING
    # --------------------------------------------------------
    
    # if datetime.datetime.now().hour > 12:
    #     target_date_obj = tomorrow
    # else:
    #     target_date_obj = today
    
    
    target_date_str = target_date_obj.strftime("%Y-%m-%d")
    print("\n-------------------****TASK START****-------------------------")
    print(f"{AIRPORT_CODE} - {target_date_str} flight selection\n")
    
    # --- fetch_flights.py ---
    print(f"[Step 1/2] Running fetch_flights.py ...")
    fetch.run_fetching(AIRPORT_CODE, target_date_obj)

    # --- filter_flights.py ---
    if WRITING_FOR_MINIPROGRAM:
        print(f"\n[Step 2/2] Running filter_flights.py for MiniProgram (JSON output) ...")
        filter.run_filterToJson(AIRPORT_CODE, target_date_obj, TARGET_MODELS_CONFIG)
    else:
        print(f"\n[Step 2/2] Running filter_flights.py ...")
        filter.run_filtering(AIRPORT_CODE, target_date_obj, TARGET_MODELS_CONFIG, FILTER_START_TIME)
    print("-------------------****TASK COMPLETE****-------------------------")
if __name__ == "__main__":
    main()