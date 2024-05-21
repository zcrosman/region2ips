import csv
import ipaddress
import argparse
from tqdm import tqdm
import math
from flask import current_app

def read_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip the header
        return list(reader)

def getDistance(coord1, coord2):
    R = 6371.0  # Radius of the Earth in kilometers
    # print(f'Before: {coord1} - {coord2}')
    lat1, lon1 = map(float, coord1)
    lat2, lon2 = map(float, coord2)
    # print(f'After: {lat1}, {lon1} - {lat2}, {lon2}')
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2_rad - lat1_rad, lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def generate_whitelist(cidr_region_data, target_loc, max_distance, custom_wl=None):
    print(f'Generating Whitelist based on loc: {target_loc} and a radius of {max_distance} km')
    # print(f'Imporing CIDR Geolocational Data...')
    # cidr_region_data = read_csv(cidr_csv_file)
    whitelist_cidr = []

    # Wrap cidr_region_data with tqdm for a progress bar
    for cidr in tqdm(cidr_region_data, desc="Processing CIDR regions"):
        cidr_loc = (cidr[7], cidr[8])
        if "" in cidr_loc:
            continue 

        d = getDistance(target_loc, cidr_loc)
        if d < max_distance:
            # print(f'CIDR: {cidr[0]} - Distance {d} Cidr: {cidr_loc}  target {target_loc}')
            whitelist_cidr.append(cidr[0])
    print(f'Whitelist inlcudes {len(whitelist_cidr)} subnets')
    if custom_wl:
        # add check if file exists
        with open(custom_wl, 'r') as file:
            for line in file:
                # Remove leading and trailing whitespaces and add the line to the list
                whitelist_cidr.append(line.strip())
 
        
    return whitelist_cidr
    

def main():
    parser = argparse.ArgumentParser(description='IP region grabber')
    parser.add_argument('--csv', required=False, help='File path to the CIDR CSV file')
    parser.add_argument('--lat', required=False, type=float, help='Latitude of the target location')
    parser.add_argument('--lon', required=False, type=float, help='Longitude of the target location')
    parser.add_argument('--max_dist', required=True, type=int, help='Maximum distance in kilometers')
    # update to be mutually exclusive to other files
    parser.add_argument('--custom-wl', required=False, type=str, help='Whitelist used to generate files (1 IP/Range per line)')

    
    args = parser.parse_args()

    cidr_csv_file_v4 = 'GeoLite2-City-CSV_20240220/GeoLite2-City-Blocks-IPv4.csv'
    target_loc = (float(args.lat), float(args.lon)) if args.lat and args.lon else (41.8919300, 12.5113300)  # Default to Rome, Italy if no location provided

    cidr_region_data = read_csv(cidr_csv_file_v4)
    
    whitelist = generate_whitelist(cidr_region_data, target_loc, args.max_dist)
    for ip in whitelist:
        print(ip)


if __name__ == "__main__":
    main()
