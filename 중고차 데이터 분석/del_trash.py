import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
from tabulate import tabulate

data = pd.read_csv("car_info_output.csv", index_col=False)
data = data[data.price != "리스승계(만원)"]

print(tabulate(data, headers='keys', tablefmt='psql', showindex=False))
#data.to_csv("filtering_data.csv",index=False, encoding = 'utf-8-sig')