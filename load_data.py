__author__ = 'frodre'

"""
General data loading functions
"""

import pandas

def query_dataframe(filters):
    pass

def grab_record_dataframe(columns):
    pass
	
def load_data_frame(data_src):
	if type(data_src) == pandas.DataFrame:
		return data_src
	else:
		pandas.read_pickle(data_src)