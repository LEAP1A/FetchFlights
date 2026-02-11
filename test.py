from FlightRadar24 import FlightRadar24API

fr_api = FlightRadar24API()

full_data = fr_api.get_airport_details('ZLXY', page=2)['airport']['pluginData']['schedule']
arrivalsList = full_data['arrivals']['data']

print(full_data)