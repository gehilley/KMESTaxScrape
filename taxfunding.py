incremental_factors_file = '2019_2020_IncrementalFactorsList.csv'
tax_pickle = 'kmes_taxes.p'
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
tax_data = p.load(open(tax_pickle,'rb'))
tax_distribution = dict()
for tax_datum in tax_data:
    apn = tax_datum[0]
    this_distribution = tax_distribution.get(apn, {})
    total_tax = tax_datum[2]
    tra = tax_datum[1]
    try:
        for key in increment_map[tra].keys():
            this_distribution[key] = increment_map[tra][key] * total_tax
    except:
        print('observed Null TRA.')

    tax_distribution[apn] = this_distribution

import numpy as np

cabrillo_total = np.sum(np.array([tax_distribution[x].get(cabrillo_key) for x in tax_distribution if
                                  tax_distribution[x].get(cabrillo_key) is not None]))

print('CUSD contributions from KMES boundary: ' + str(cabrillo_total))

p.dump([tax_distribution, funding_code_map], open(distribution_pickle_out,'wb'))

