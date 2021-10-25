from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.coingecko.com/en/coins/ethereum/historical_data/usd?start_date=2020-01-01&end_date=2021-06-30#panel')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table_ethereum = soup.find('table', attrs={'class': 'table table-striped text-sm text-lg-normal'})
row = table_ethereum.find_all('th', attrs={'class':'font-semibold text-center'})
row_length = len(row)

temp = [] #initiating a list 

#insert the scrapping process here
#get date 
for table_rows in table_ethereum.find_all('tr'):
    # Find Header Date
    header_date = table_rows.find('th', attrs={'class': 'font-semibold text-center'})
    if(header_date) != None:
        periode = header_date.text.replace("-", "/")
    
    #get volume
    column_iteration = 0
    for table_columns in table_rows.find_all('td'):
        
        if (column_iteration) == 0:
            market_cap = table_columns.text.replace("$", "").replace(",", "").strip()
        elif (column_iteration) == 1:
            volume = table_columns.text.replace("$", "").replace(",", "").strip()
        elif (column_iteration) == 2:
            open_price = table_columns.text.replace("$", "").replace(",", "").strip()
        elif (column_iteration) == 3:
            close = table_columns.text.replace("$", "").replace(",", "").strip()
        if column_iteration == 3:
            temp.append((periode,market_cap,volume,open_price,close))      
        column_iteration += 1
    
temp = temp[::-1]

#change into dataframe
df_ethereum = pd.DataFrame(temp, columns = ('periode','market_cap','volume', 'open_price', 'close'))

#insert data wrangling here
df_ethereum['periode'] = df_ethereum['periode'].astype('datetime64')
df_ethereum['market_cap'] = df_ethereum['market_cap'].astype('float64')
df_ethereum['volume'] = df_ethereum['volume'].astype('float64')
df_ethereum['open_price'] = df_ethereum['open_price'].astype('float64')
df_ethereum.dtypes

#changing periode as index to make it as the x-axis when plotting
df_ethereum = df_ethereum.set_index('periode')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df_ethereum["volume"].mean()} #be careful with the " and ' 

	# generate plot
	ax = df_ethereum.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)