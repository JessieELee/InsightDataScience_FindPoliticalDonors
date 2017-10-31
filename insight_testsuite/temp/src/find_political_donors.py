#!/usr/bin/env python

import sys
import numpy as np
import pandas as pd


def by_zip(input_path, by_zip_path):
    input_file = open(input_path, 'r')
    by_zip_file = open(by_zip_path, 'w+')
    input_file_by_line = input_file.readlines()
    dict_by_zip = {}

    for each_line in input_file_by_line:
        each_line_split = each_line.split('|')
        if (each_line_split[0] != '') and (each_line_split[14] != '') and (each_line_split[15] == '') and (len(each_line_split[10]) > 4):
            zipcode = each_line_split[10][0:5]
            name_and_zip = each_line_split[0] + zipcode
            if name_and_zip in dict_by_zip:
                dict_by_zip[name_and_zip].append(int(each_line_split[14]))
            else:
                dict_by_zip[name_and_zip] = [int(each_line_split[14])]
            line_to_write = each_line_split[0] + '|' + zipcode + '|' + str(int(round(np.median(dict_by_zip[name_and_zip])))) + '|' + str(len(dict_by_zip[name_and_zip])) + '|' + str(sum(dict_by_zip[name_and_zip])) + '\n'
            by_zip_file.write(line_to_write)

    by_zip_file.close()


def by_date(input_path, by_date_path):
    raw_data = pd.read_table(input_path, header=None)
    raw_data = raw_data[0].apply(lambda x: x.split('|'))
    wanted_data = [raw_data.apply(lambda x: x[0]), raw_data.apply(lambda x: x[13]), raw_data.apply(lambda x: x[14]), raw_data.apply(lambda x: x[15])]
    wanted_data = np.swapaxes(np.array(wanted_data), 0, 1)
    wanted_data = pd.DataFrame(wanted_data, columns='CMTE_ID TRANSACTION_DT TRANSACTION_AMT OTHER_ID'.split())
    wanted_data = wanted_data[wanted_data['OTHER_ID'] == '']
    wanted_data.drop('OTHER_ID', axis=1, inplace=True)
    wanted_data = wanted_data[wanted_data['TRANSACTION_DT'].apply(lambda x: len(x) == 8)]
    wanted_data = wanted_data[wanted_data['TRANSACTION_DT'].apply(lambda x: 0 < int(x[0:2]) < 13 and 0 < int(x[2:4]) < 32)]
    wanted_data['TRANSACTION_AMT'] = wanted_data['TRANSACTION_AMT'].apply(lambda x: int(x))
    group_sum = wanted_data.groupby(['CMTE_ID', 'TRANSACTION_DT']).sum().round()
    group_sum = group_sum.rename(columns={'TRANSACTION_AMT': 'sum'})
    group_sum['sum'] = group_sum['sum'].apply(lambda x: int(x))
    group_median = wanted_data.groupby(['CMTE_ID', 'TRANSACTION_DT']).median().round()
    group_median = group_median.rename(columns={'TRANSACTION_AMT': 'median'})
    group_median['median'] = group_median['median'].apply(lambda x: int(x))
    group_count = wanted_data.groupby(['CMTE_ID', 'TRANSACTION_DT']).count()
    group_count = group_count.rename(columns={'TRANSACTION_AMT': 'count'})
    group_data = group_median.join(group_sum).join(group_count)
    group_data = group_data.reset_index().sort_values(by=['CMTE_ID', 'TRANSACTION_DT'])

    by_date_file = open(by_date_path, 'w+')

    for index, row in group_data.iterrows():
        by_date_file.write(row['CMTE_ID']+'|'+row['TRANSACTION_DT']+'|'+str(row['median'])+'|'+str(row['count'])+'|'+str(row['sum'])+'\n')

    by_date_file.close()


if __name__ == '__main__':
    input_path = sys.argv[1]
    by_zip_path = sys.argv[2]
    by_date_path = sys.argv[3]
    by_zip(input_path, by_zip_path)
    by_date(input_path, by_date_path)
