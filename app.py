# TODO css gray out and disable download unless available
# Additional filter for country state?
# limit results shown to first 200 to prevent crashing
# gen warning with large radius


from flask import Flask, render_template, request, jsonify, current_app
from region2ip import generate_whitelist, read_csv
import os

app = Flask(__name__, template_folder='html')

cidr_csv_file = 'GeoLite2-City-CSV_20240220/GeoLite2-City-Blocks-IPv4.csv'

app.config['CIDR_REGION_DATA'] = None

with app.app_context():
    print('Loading CIDR Geolocational Data. This should take 5-10 sec')
    print(' Web page will start shortly after it is loaded.\n')
    # Load the data and store it in app.config
    app.config['CIDR_REGION_DATA'] = read_csv(cidr_csv_file)
    print('Data loaded successfully.')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_whitelist', methods=['GET'])
def web_generate_whitelist():
    # Use the stored location and radius, or default values if not set
    target_loc = app.config.get('TARGET_LOCATION', (36.174465, -86.767960))  # Default: Rome, Italy
    max_distance = app.config.get('MAX_DISTANCE', 100)  # Default: 100 kilometers
    cidr_region_data = app.config['CIDR_REGION_DATA']  # Use preloaded CIDR region data

    # Generate whitelist with full results
    full_whitelist_cidr = generate_whitelist(cidr_region_data, target_loc, float(max_distance))
    
    # Save full results to a file
    full_temp_file_path = "static/full_whitelist.txt"
    with open(full_temp_file_path, 'w', encoding='utf-8') as file:
        for cidr in full_whitelist_cidr:
            file.write(cidr + "\n")

    # Return only the first 500 results
    limited_whitelist_cidr = full_whitelist_cidr[:500]

    # Save limited results to another file
    limited_temp_file_path = "static/limited_whitelist.txt"
    with open(limited_temp_file_path, 'w', encoding='utf-8') as file:
        for cidr in limited_whitelist_cidr:
            file.write(cidr + "\n")

    # Indicator if the response was limited or not
    response_indicator = "limited" if len(full_whitelist_cidr) > 500 else "not limited"

    return jsonify({
        "whitelist": limited_whitelist_cidr,
        "whitelist_len": len(full_whitelist_cidr),
        "response_indicator": response_indicator

    })
    
    
@app.route('/api/location', methods=['POST'])
def location():
    data = request.get_json()
    lat = data['lat']
    lng = data['lng']
    # Store the latitude and longitude in app.config
    app.config['TARGET_LOCATION'] = (lat, lng)
    return jsonify({"status": "success", "lat": lat, "lng": lng})

@app.route('/api/radius', methods=['POST'])
def update_radius():
    data = request.get_json()
    radius_km = data.get('radiusKm')
    # Store the radius in app.config
    app.config['MAX_DISTANCE'] = radius_km
    return jsonify({"status": "success", "message": "Radius updated"}), 200


@app.route('/api/last_coordinates')
def get_last_coordinates():
    # Retrieve the last set coordinates from wherever they are stored in your application
    # For example, if you are storing them in a global variable or in the database
    last_coordinates = {
        "lat": app.config.get('LAST_LATITUDE', 36.174465),
        "lng": app.config.get('LAST_LONGITUDE', -86.767960),
        "zoom": app.config.get('LAST_ZOOM', 7)
    }
    return jsonify(last_coordinates)

@app.route('/api/last_radius')
def get_last_radius():
    # Retrieve the last set radius value from wherever it is stored in your application
    # For example, if you are storing it in a global variable or in the database
    last_radius = {
        "radius": app.config.get('LAST_RADIUS', 200)
    }
    return jsonify(last_radius)


if __name__ == '__main__':
    app.run(debug=True, port=8888)