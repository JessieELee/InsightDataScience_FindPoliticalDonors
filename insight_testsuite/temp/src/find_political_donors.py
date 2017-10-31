#!/usr/bin/env python

import sys
import numpy as np
import pandas as pd


# SORT BY ZIPCODE

def by_zip(input_path, by_zip_path):
    input_file = open(input_path, 'r')
    by_zip_file = open(by_zip_path, 'w+')

    # Read in the file line by line.
    input_file_by_line = input_file.readlines()

    # Start an empty dictionary.
    dict_by_zip = {}

    for each_line in input_file_by_line:
        # Turn the input line into a list using | as the delimeter.
        each_line_split = each_line.split('|')

        # Make sure that the CMTE_ID and TRANSACTION_AMT aren't empty, and that make sure to look at only individual contributions,
        # i.e. OTHER_ID is empty. Also, ignore data with empty or zipcode that's too short (less than 5 digits). Date is
        # not taken into account for this first part of the challenge.
        if (each_line_split[0] != '') and (each_line_split[14] != '') and {int(each_line_split[14]) > 0} and (each_line_split[15] == '') and (len(each_line_split[10]) > 4):

            # Get the first five digits of zipcode.
            zipcode = each_line_split[10][0:5]

            # Create a unique CMTE_ID+zipcode key for the dictionary.
            name_and_zip = each_line_split[0] + zipcode

            # Add the TRAMSACTION_AMT to the list of donation amounts for this specific recipieint at this zipcode.
            if name_and_zip in dict_by_zip:
                dict_by_zip[name_and_zip].append(int(each_line_split[14]))
            else:
                dict_by_zip[name_and_zip] = [int(each_line_split[14])]

            # Create the record and write to the text file. (CMTE_ID|zipcode|median|count|sum)
            line_to_write = each_line_split[0] + '|' + zipcode + '|' + str(int(round(np.median(dict_by_zip[name_and_zip])))) + '|' + str(len(dict_by_zip[name_and_zip])) + '|' + str(sum(dict_by_zip[name_and_zip])) + '\n'
            by_zip_file.write(line_to_write)

    by_zip_file.close()


# Check the date range and format. Make sure it's correct. This function is only used in by_date(input_path, by_date_path)
def check_date(date):

    # Maka sure the length is correct. The format is mmddyyyy is there should always be 8 digits.
    if len(date) == 8:

        # Extract the month, day, and year from the string.
        mon = date[0:2]
        day = date[2:4]
        year = date[4:8]

        # The year should be greater than 1775 and less than 2018.
        if 1775 < int(year) < 2018:

            # January, March, May, July, August, October, and December has 31 days in the month.
            if mon in ['01', '03', '05', '07', '08', '10', '12'] and int(day) < 32:
                return True
            # April, June, September, and November has 30 days in the month.
            elif mon in ['04', '06', '09', '11'] and int(day) < 31:
                return True
            # For Feburary:
            elif mon == '02':
                # Leap years have 29 days in the month.
                if int(year) % 4 == 0:
                    if int(day) < 30:
                        return True
                    else:
                        return False
                # Non leap years have 28 days in the month.
                else:
                    if int(day) < 29:
                        return True
                    else:
                        return False
            else:
                return False
        else:
            return False
    else:
        return False


# SORT BY DATE
def by_date(input_path, by_date_path):

    # Read all the data in as a table
    raw_data = pd.read_table(input_path, header=None)

    # Use | as the delimeter to parse the data.
    raw_data = raw_data[0].apply(lambda x: x.split('|'))

    # Get the wanted info: CMTE_ID, TRANSACTION_DT, TRANSACTION_AMT, and OTHER_ID.
    wanted_data = [raw_data.apply(lambda x: x[0]), raw_data.apply(lambda x: x[13]), raw_data.apply(lambda x: x[14]), raw_data.apply(lambda x: x[15])]

    # Swap the axes to make a proper array for DataFrame. Now each row is a new record.
    wanted_data = np.swapaxes(np.array(wanted_data), 0, 1)

    # Create the DataFrame with the columns CMTE_ID, TRANSACTION_DT, TRANSACTION_AMT, and OTHER_ID.
    wanted_data = pd.DataFrame(wanted_data, columns='CMTE_ID TRANSACTION_DT TRANSACTION_AMT OTHER_ID'.split())

    # Only look at individual contributers, i.e. OTHER_ID is empty.
    wanted_data = wanted_data[wanted_data['OTHER_ID'] == '']

    # Remove the OTHER_ID column since it's no longer needed.
    wanted_data.drop('OTHER_ID', axis=1, inplace=True)

    # Make sure that CMTE_ID, TRANSACTION_DT, and TRANSACTION_AMT are not empty. Ignore the record if any of these is
    # empty.
    wanted_data = wanted_data[wanted_data['CMTE_ID'] != '']
    wanted_data = wanted_data[wanted_data['TRANSACTION_DT'] != '']
    wanted_data = wanted_data[wanted_data['TRANSACTION_AMT'] != '']

    # Check the date format: make sure that it's the right length (mmddyyyy)
    #wanted_data = wanted_data[wanted_data['TRANSACTION_DT'].apply(lambda x: len(x) == 8)]

    # Make sure the month is a number between 1 and 12, and the day is a number between 1 and 31.
    #wanted_data = wanted_data[wanted_data['TRANSACTION_DT'].apply(lambda x: 0 < int(x[0:2]) < 13 and 0 < int(x[2:4]) < 32)]

    wanted_data = wanted_data[wanted_data['TRANSACTION_DT'].apply(lambda x: check_date(x))]
    # Make the TRANSACTION_AMT integers so calculations can be performed on the numbers. Ignore if the TRANSACTIOIN_AMT
    # is negative.
    wanted_data['TRANSACTION_AMT'] = wanted_data['TRANSACTION_AMT'].apply(lambda x: int(x))
    wanted_data = wanted_data[wanted_data['TRANSACTION_AMT'] > 0]

    # Group the data be CMRE_ID and TRANSACTION_DT. Get the:
    # 1. sum
    group_sum = wanted_data.groupby(['CMTE_ID', 'TRANSACTION_DT']).sum().round()
    group_sum = group_sum.rename(columns={'TRANSACTION_AMT': 'sum'})
    group_sum['sum'] = group_sum['sum'].apply(lambda x: int(x))

    # 2. median
    group_median = wanted_data.groupby(['CMTE_ID', 'TRANSACTION_DT']).median().round()
    group_median = group_median.rename(columns={'TRANSACTION_AMT': 'median'})
    group_median['median'] = group_median['median'].apply(lambda x: int(x))

    # 3. and the count (number of transactions)
    group_count = wanted_data.groupby(['CMTE_ID', 'TRANSACTION_DT']).count()
    group_count = group_count.rename(columns={'TRANSACTION_AMT': 'count'})

    # Join all the indivicual DataFrames. The resulting DataFrame contains the CMTE_ID and TRANSACTION_DT with the corresponding
    # sum, median, and count info.
    group_data = group_median.join(group_sum).join(group_count)

    # Sort the records so that the CMTE_ID is alphabetical and the TRANSACTION_DT is chronological.
    group_data = group_data.reset_index().sort_values(by=['CMTE_ID', 'TRANSACTION_DT'])

    # Start the output file.
    by_date_file = open(by_date_path, 'w+')

    # Iterate through each row of the DataFrame and write the records into the text file. (CMTE_ID|TRANSACTION_DT|median|count|sum)
    for index, row in group_data.iterrows():
        by_date_file.write(row['CMTE_ID']+'|'+row['TRANSACTION_DT']+'|'+str(row['median'])+'|'+str(row['count'])+'|'+str(row['sum'])+'\n')

    by_date_file.close()


# The main function: Get the input_path (first argument), the path to mediainvals_by_zip.txt (second argument),
# and the path to medianvals_by_date.txt (third argument).
if __name__ == '__main__':
    input_path = sys.argv[1]
    by_zip_path = sys.argv[2]
    by_date_path = sys.argv[3]

    # SORT BY ZIPCODE
    by_zip(input_path, by_zip_path)

    # SORT BY DATE
    by_date(input_path, by_date_path)
