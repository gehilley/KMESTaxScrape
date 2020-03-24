incremental_factors_file = '../2019_2020_IncrementalFactorsList.csv'
tax_pickle_for_apns = 'kmes_taxes.p'
tax_history_pickle = '../cusd_1percent_tax_history.p'
distribution_pickle_out = 'kmes_distribution.p'
cabrillo_key = 50200

def read_incremental_factors():
    import csv
    inc_file = open(incremental_factors_file, 'r')
    reader = csv.reader(inc_file)
    increment_map = dict()
    funding_code_map = dict()
    this_trn_code = ''
    for row in reader:
        if row[0] != '':
            this_trn_code = row[0].replace('-','')
        this_trn = increment_map.get(this_trn_code,{})
        this_trn[int(row[1])] = float(row[3])
        funding_code_map[int(row[1])] = row[2]
        increment_map[this_trn_code] = this_trn
    return increment_map, funding_code_map

increment_map, funding_code_map = read_incremental_factors()
import pickle as p
tax_data_apns = p.load(open(tax_pickle_for_apns,'rb'))
apns = list(set([d[0] for d in tax_data_apns]))
apns.sort()
tax_distribution = list()
tax_history = p.load(open(tax_history_pickle,'rb'))
tax_history_apns = [d[0] for d in tax_history]

for apn in apns:
    try:
        tax_history_index = tax_history_apns.index(apn)
    except:
        tax_history_index = None
    if tax_history_index is None:
        print('No Matching APN: ' + apn)
    else:
        this_tax_history = tax_history[tax_history_index]
        total_tax = this_tax_history[3]
        tra = this_tax_history[1]
        this_tra = increment_map.get(tra, None)
        if this_tra is None:
            print('TRA is Null for APN: ' + apn)
        else:
            fraction = this_tra.get(cabrillo_key, None)
            if fraction is None:
                print('APN: ' + apn + ' is not in district')
            else:
                tax_distribution += [[this_tax_history[0], this_tax_history[1], this_tax_history[2], fraction, this_tax_history[3], [t*fraction for t in this_tax_history[3]]]]

import numpy as np

district_data = np.array(np.array([x[5] for x in tax_distribution]))

print('District Contributions: ')

district_sum = np.sum(district_data, axis=0)
year = 2007
for ds in district_sum:
    print(str(year) + ": " + str(ds))
    year += 1

p.dump([tax_distribution, funding_code_map], open(distribution_pickle_out,'wb'))

