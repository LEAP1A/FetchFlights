import datetime
import fetch_flights as fetch  # fetch_flights.py
import filter_flights as filter  # filter_flights.py

# ================= CONFIGURATION =================

# Target Airport ICAO
AIRPORT_CODE = "VHHH" 

TARGET_MODELS_CONFIG = [
     "A19N", "A330", "A332", "A333","A339", "A359", "B733", "B734", "B752", "B763", "B772", "B77L", "B77W", "B788", "B789", "B744", "AJ27", "C919", "IL76", 
     "330", "332", "333", "359", "739", "73F", "75F", "76F", "77F", "77L", "773", "77W", "777", "788", "789", "744", "C09", "909", "919"
]

FILTER_START_TIME = "00:00"

# ======================================================================
def main():
    
    # --- Calculate the target day ---
    # 逻辑: 中午12点后，目标日期是明天；否则是今天。
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    if datetime.datetime.now().hour > 12:
        target_date_obj = tomorrow
    else:
        target_date_obj = today
    
    target_date_str = target_date_obj.strftime("%Y-%m-%d")
    print("\n-------------------****TASK START****-------------------------")
    print(f"{AIRPORT_CODE} - {target_date_str} flight selection\n")
    
    # --- fetch_flights.py ---
    print(f"[Step 1/2] Running fetch_flights.py ...")
    fetch.run_fetching(AIRPORT_CODE, target_date_obj)

    # --- filter_flights.py ---
    print(f"\n[Step 2/2] Running filter_flights.py ...")
    filter.run_filtering(AIRPORT_CODE, target_date_str, TARGET_MODELS_CONFIG, FILTER_START_TIME)
    print("-------------------****TASK COMPLETE****-------------------------")
if __name__ == "__main__":
    main()