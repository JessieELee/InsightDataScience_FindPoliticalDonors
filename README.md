# InsightDataScience_FindPoliticalDonors
Insight Data Science Coding Challenge: Find political donors

Python 3.6.1 :: Anaconda 4.4.0 (x86_64)
IMPORTED LIBRARIES: sys, numpy, pandas


GENERAL STRATEGIES:

* Sort by zipcode: Read the file line by line. Create a dictionary to store the running donation amounts as lists
using (recipient ID + zipcode) as keys. Add the new amount to the list and calculate the updated median and sum as a new
line is read.


* Sort by date: Read in the data as a table. Use the relavent fields to create a DataFrame. Group the data by recipient
and by date, and then sort the data so that the recipient ID are in alphabetical order, and then the dates are in chronological
order.



TO RUN:

Once run.sh is executable (chmod +x run.sh), simply type ./run.sh
