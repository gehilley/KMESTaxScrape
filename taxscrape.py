output_filename = 'kings_mountain_taxes.csv'
base_url = "https://gis.smcgov.org/maps/rest/services/WEBAPPS/COUNTY_SAN_MATEO_TKNS/MapServer/identify"
token = "YQhTpcG1-kkLM8npEXzgdzmpHcrypfaAq2_vG28QQk0."
polygon = [(-13622312.48,4506393.674),
           (-13622866.64,4504129.241),
           (-13622054.51,4501702.363),
           (-13622081.51,4500703.546),
           (-13622336.7,4500699.901),
           (-13622209.69,4500208.989),
           (-13620628.37,4498576.899),
           (-13620855.91,4496456.415),
           (-13621178.77,4496056.135),
           (-13620850.69,4493901.594),
           (-13619861.84,4493897.488),
           (-13619569,4490187.675),
           (-13619905.81,4489530.952),
           (-13619314.07,4488339.813),
           (-13618317.52,4488701.441),
           (-13618258.04,4488474.013),
           (-13615983.9,4488310.236),
           (-13615652.87,4488885.978),
           (-13615005.01,4489100.013),
           (-13613917.21,4488836.71),
           (-13613914.39,4488379.079),
           (-13612911.75,4488366.21),
           (-13612888.41,4494314.066),
           (-13615097.8,4495888.695),
           (-13615271.32,4496853.081),
           (-13616508.99,4497514.873),
           (-13616383.3,4498273.144),
           (-13615602.16,4498927.021),
           (-13616669.94,4499925.725),
           (-13617650.42,4501543.218),
           (-13618538.41,4501849.55),
           (-13619271.78,4503718.206),
           (-13620684.15,4505168.724),
           (-13620959.32,4506823.444),
           (-13622312.48,4506393.674)]
sr = 102100
tax_base_url = 'https://sanmateo-ca.county-taxes.com/public/search'
tax_bill_url = 'https://sanmateo-ca.county-taxes.com'
tax_link_contents = '2019 Secured Annual Bill'
tax_key_bond = 'Cabrillo Usd Bond'
tax_key_B = 'CAB USD MEAS B 2015-20'

def get_apns(extent, plot_boundaries = True):
    (xmin, ymin, xmax, ymax) = extent
    from shapely.geometry import Polygon
    p1 = Polygon(polygon)
    p2 = Polygon([(xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin), (xmin, ymax)])
    p3 = p1.intersection(p2)
    try:
        coords = list(p3.exterior.coords)
    except:
        coords = []
    if plot_boundaries:
        from matplotlib import pylab as plt
        plt.ion()
        plt.figure(1)
        for i in range(len(coords)-1):
            plt.plot([coords[i][0], coords[i+1][0]], [coords[i][1], coords[i+1][1]], 'b-')
        plt.axis('equal')
    geometry = '{"rings": [[' + ','.join(['[' + str(c[0]) + ',' + str(c[1]) + ']' for c in coords]) + ']]}'
    import requests
    payload = {"token": token,
               "f": "json",
               "tolerance": 0,
               "returnGeometry": "false",
               "geometry": geometry,
               "geometryType": "esriGeometryPolygon",
               "sr": sr,
               "mapExtent": "{xmin}, {ymin}, {xmax}, {ymax}".format(xmin = xmin, ymin = ymin, xmax = xmax, ymax = ymax),
               "layers": "visible:0",
               "imageDisplay": "572%2C774%2C96"}
    r = requests.get(base_url,params=payload)
    records = r.json()
    if records.get('exceededTransferLimit', None) is not None:
        print('WARNING: Transfer limit exceeded.  Reduce square size')
    return [s['attributes']['NOGEOMAPN'] for s in records['results']]

def collect_all_apns(square_size = 5000, plot_boundaries = True):
    x, y = zip(*polygon)
    (minx, maxx, miny, maxy) = (min(x), max(x), min(y), max(y))
    import math
    apns = set()
    for i in range(math.ceil((maxy-miny)/square_size)):
        tile_y_min = square_size * float(i) + miny
        tile_y_max = square_size * float(i+1) + miny if square_size * float(i+1) + miny < maxy else maxy
        for j in range(math.ceil((maxx-minx)/square_size)):
            tile_x_min = square_size * float(j) + minx
            tile_x_max = square_size * float(j+1) + minx if square_size * float(j+1) + minx else maxx
            extent = (tile_x_min, tile_y_min, tile_x_max, tile_y_max)
            this_apns = get_apns(extent, plot_boundaries=plot_boundaries)
            apns.update(this_apns)
    return apns

def get_tax_record(apn):
    payload = {"search_query":apn,
               "category":all}
    import requests
    r = requests.get(tax_base_url, params=payload)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.content, features="html.parser")
    a_tags = soup.find_all('a')
    clickthrough = None
    for tag in a_tags:
        if tax_link_contents in tag.contents[0]:
            clickthrough = tag['href']
    bond_tax = 0
    b_tax = 0
    if clickthrough is not None:
        r = requests.get(tax_bill_url + clickthrough)
        soup = BeautifulSoup(r.content, features="html.parser")
        td_tax_bond = soup.find("td", text=tax_key_bond)
        if td_tax_bond is not None:
            bond_tax = float(td_tax_bond.find_next_sibling("td").find_next_sibling("td")\
                .find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text.replace('$','').replace(',',''))
        else:
            bond_tax = 0
        td_B_tax = soup.find("td", text=tax_key_B)
        if td_B_tax is not None:
            b_tax = float(td_B_tax.find_next_sibling("td").text.replace('$','').replace(',',''))
    return bond_tax, b_tax

data = list()
APNs = list(collect_all_apns())
APNs.sort()

total = len(APNs)
counter = 1
for APN in APNs:
    print('{counter} / {total}'.format(counter = counter, total = total))
    bond_tax, b_tax = get_tax_record(APN)
    this_APN = APN[0:3] + '-' + APN[3:6] + '-' + APN[6:]
    data.append([this_APN, bond_tax, b_tax])
    counter += 1

import csv
with open(output_filename, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in data:
        writer.writerow(row)

