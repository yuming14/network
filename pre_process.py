import pandas as pd
got_data = pd.read_csv('network_vec.csv', sep='\s+', nrows = 100000)
got_data.to_csv("network_vec_small.csv",index=False,sep=',')
#got_data = pd.read_csv('network_vec_small.csv')
#print(got_data)