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
    
    # Logic to decide date range
    if datetime.datetime.now().hour > 12:
        target_date_str = tomorrow.strftime("%Y-%m-%d")
    else:
        target_date_str = today.strftime("%Y-%m-%d")
        
    # File Names
    csvFileName = f"{airport_code}_{target_date_str}_arrivals.csv"  
    outputFileName = f"{airport_code}_{target_date_str}_selected_arrivals.md" # Changed to .md

    count = 0
    try:
        with open(csvFileName, 'r', encoding='utf-8') as f_in, \
             open(outputFileName, 'w', encoding='utf-8') as f_out:
            
            reader = csv.reader(f_in)
            
            # 1. Write Markdown Title and Table Header
            f_out.write(f"# {airport_code} - {target_date_str} Selected Flights\n\n")
            # Markdown table syntax
            f_out.write("| Flight | Airline | Arrival Time | Origin | Model | Reg |\n")
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

                # --- Filter 1: Airline check ---
                if "(" in airline_name:
                    is_selected = True
                    disp_airline = f"**{airline_name}**"  # Highlight Airline Column

                # --- Filter 2: Model check ---
                if model_code in TARGET_MODELS:
                    is_selected = True
                    disp_model = f"**{model_code}**" # Highlight Model Column

                # --- Filter 3: Registration check ---
                if registration != "N/A":
                    if not re.match(r"^B-\d", registration):
                        is_selected = True
                        disp_reg = f"**{registration}**" # Highlight Registration Column

                # --- Write row if selected ---
                if is_selected:
                    # Construct Markdown table row using pipes |
                    line = f"| {flight_num} | {disp_airline} | {arrival_time} | {origin_code} | {disp_model} | {disp_reg} |\n"
                    f_out.write(line)
                    count += 1

        print(f"Done! Found {count} flights. Saved to {outputFileName}")
        print("Tip: Open the .md file in VS Code and press 'Ctrl + Shift + V' to see the pretty table.")

    except FileNotFoundError:
        print(f"Error: The file '{csvFileName}' was not found. Please check the filename.")

if __name__ == "__main__":
    main()