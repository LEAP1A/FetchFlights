import csv
import re 
import datetime

# ================= CONFIGURATION =================
airport_code = "ZLXY" # ICAO

# Target Aircraft Models 
TARGET_MODELS = [
     "A19N", "A332", "A333","A339", "A359", "B733", "B734", "B752", "B763", "B772", "B77L", "B77W", "B788", "B789", "B744", "AJ27", "C919", "IL76", 
     "330", "332", "333", "359", "739", "73F", "75F", "76F", "77F", "77L", "773", "77W", "777", "788", "789", "744", "C09", "909", "919"
]
# =============================================

def main():
    
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    if datetime.datetime.now().hour > 12:
        target_date_str = tomorrow.strftime("%Y-%m-%d")
    else:
        target_date_str = today.strftime("%Y-%m-%d")
    # File Names
    csvFileName = f"{airport_code}_{target_date_str}_arrivals.csv"  

    outputFileName = f"{airport_code}_{target_date_str}_selected_arrivals.txt"
    count = 0
    try:
        with open(csvFileName, 'r', encoding='utf-8') as f_in, \
             open(outputFileName, 'w', encoding='utf-8') as f_out:
            
            reader = csv.reader(f_in)
            
            # Write Header to the output TXT file
            header = f"{'Flight':<10} | {'Airline':<40} | {'Arrival Time':<20} | {'Origin':<8} | {'Model':<8} | {'Reg'}\n"
            f_out.write(header)
            f_out.write("-" * 105 + "\n")

            for row in reader:
                # Skip empty lines if any
                if not row:
                    continue
                
                # Unpack the row (CSV columns: Flight, Airline, Time, Origin, Model, Reg)
                flight_num = row[0]
                airline_name = row[1]
                arrival_time = row[2]
                origin_code = row[3]
                model_code = row[4]
                registration = row[5]

                # Initialize a flag
                is_selected = False

                # --- Filter 1: Airline string contains "(" ---
                if "(" in airline_name:
                    is_selected = True

                # --- Filter 2: Model is in the target list ---
                if model_code in TARGET_MODELS:
                    is_selected = True

                # --- Filter 3: Registration check --- USED ONLY FOR MAINLAND CHINA AIRPORT TO EXCLUDE CAAC A/C
                # We want to keep it if it is NOT a standard mainland China reg (B-1234)
                # Regex explanation: ^B-\d means "Starts with B- then a digit"
                # If it matches, it's standard. We select if it does NOT match.
                # Also ensure registration is not "N/A" before checking
                if registration != "N/A":
                    if not re.match(r"^B-\d", registration):
                        is_selected = True

                # --- Write to file if selected ---
                if is_selected:
                    line = f"{flight_num:<10} | {airline_name[:40]:<40} | {arrival_time:<20} | {origin_code:<8} | {model_code:<8} | {registration}\n"
                    f_out.write(line)
                    count += 1

        print(f"Done! Found {count} flights matching criteria. Saved to {outputFileName}")

    except FileNotFoundError:
        print(f"Error: The file '{csvFileName}' was not found. Please check the filename.")

if __name__ == "__main__":
    main()
