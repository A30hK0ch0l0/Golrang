b, c = input("Enter your number of bins and clusters like 'b,c': ").split(',')
b, c = int(b), int(c)

import pandas as pd
import dataframe_image as dfi
import numpy as np
from rfm import RFM
import jenkspy
import matplotlib
import matplotlib.pyplot as plt
from IPython.core.pylabtools import figsize

pd.set_option('colheader_justify', 'center')

data = pd.read_csv('sample_data.csv')
data = data.astype({'date': 'datetime64[ns]'})
data['day_of_week'] = data['date'].dt.day_name()

data_date = data.groupby(['day_of_week', 'date']).agg({'total_purchase': 'count'})

index_title = ['روز هفته']
hafte = ['شنبه', 'یکشنبه', 'دوشنبه' ,'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه']
amargan = ['میانگین تقاضای روزانه', 'انحراف معیار تقاضای روزانه']
daily = pd.DataFrame(columns=amargan, index=hafte).rename_axis(index_title)

days = data['day_of_week'].unique()
week = [days[(i+np.where(days == 'Saturday')[0])%7][0] for i in range(len(days))]
hafte2week = dict(zip(hafte, week))

for day in daily.index:
    data_day = data_date.query('day_of_week=="{}"'.format(hafte2week[day]))
    mean_std = [data_day['total_purchase'].mean(), data_day['total_purchase'].std()]
    daily.loc[day] = pd.Series(dict(zip(daily.columns, mean_std)))

daily = daily.style.set_table_styles([dict(selector='th',\
        props=[('text-align', 'center'),('background-color', '#40466e'),('color', 'white')])])
daily.set_properties(**{'text-align': 'center'})

dfi.export(daily, 'amargan' + ".png")

matplotlib.rcParams['font.size'] = 10
matplotlib.rcParams['figure.dpi'] = 100
 
figsize(16, 9)

purchase_count = pd.DataFrame(data['total_purchase'].value_counts())
purchase_anomaly = purchase_count[purchase_count['total_purchase'] == 1].index.min()
data['purchase_normalized'] = data['total_purchase'].apply(lambda purchace: min(purchase_anomaly, purchace))
purchase_count_new = pd.DataFrame(data['purchase_normalized'].value_counts())

we = ['WorkingDays', 'WeekEnd']
data['work_end'] = data['day_of_week'].apply(lambda day: we[week.index(day)//5])

x1 = list(data[data['work_end'] == 'WeekEnd'    ]['purchase_normalized'])
x2 = list(data[data['work_end'] == 'WorkingDays']['purchase_normalized'])
 
colors=['pink', 'blue']
names=['WeekEnd', 'WorkingDays']

plt.hist([x1, x2], color=colors, label=names, density=False, bins=b)

plt.legend()
plt.title('HistoGram of Demand')
plt.xlabel('Demand')

plt.savefig('hist.png')

r = RFM(data, customer_id='user_id', transaction_date='date', amount='total_purchase')
rfm_table = r.rfm_table.iloc[:, :4]

rfm_table['R_rank'] = rfm_table['recency'].rank(ascending=False)
rfm_table['F_rank'] = rfm_table['frequency'].rank(ascending=True)
rfm_table['M_rank'] = rfm_table['monetary_value'].rank(ascending=True)

rfm_table['R_rank_norm'] = (rfm_table['R_rank']/rfm_table['R_rank'].max())
rfm_table['F_rank_norm'] = (rfm_table['F_rank']/rfm_table['F_rank'].max())
rfm_table['M_rank_norm'] = (rfm_table['M_rank']/rfm_table['M_rank'].max())

rfm_table.drop(columns=['R_rank', 'F_rank', 'M_rank'], inplace=True)

rfm_table['RFM_Score'] =\
0.45*rfm_table['R_rank_norm']+0.46*rfm_table['F_rank_norm']+0.09*rfm_table['M_rank_norm']

breaks = jenkspy.jenks_breaks(rfm_table['RFM_Score'], c)
rfm_table['cluster'] = pd.cut(rfm_table['RFM_Score'],
                              bins=breaks,
                              labels=['Cluster_{}'.format(i+1) for i in range(c)],
                              include_lowest=True)

index_title = ['گروه مشتریان']
clusters = ['خوشه {}'.format(i+1) for i in range(c)]
amargan = ['Ave. R', 'Ave. F', 'Ave. M']
clustering = pd.DataFrame(columns=amargan, index=clusters).rename_axis(index_title)

for cluster in clustering.index:
    clustering_cluster = rfm_table[rfm_table['cluster']=='Cluster_{}'.format(cluster[-1])]
    averages = [clustering_cluster[RFM].mean() for RFM in clustering_cluster.columns[1:4]]
    clustering.loc[cluster] = pd.Series(dict(zip(clustering.columns, averages)))

clustering = clustering.style.set_table_styles([dict(selector='th',\
             props=[('text-align', 'center'),('background-color', '#40466e'),('color', 'white')])])
clustering.set_properties(**{'text-align': 'center'})

dfi.export(clustering, 'clustering' + ".png")

rfm_table.plot.scatter(x='frequency', y='recency', c='cluster',
                       colormap='viridis', marker='$.$', s=7777)

plt.savefig('scatter.png')

htmlstring = """
<html>

    <head>

        <title>
            PythonAnywhere hosted web application
        </title>

        <style>
            * {
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }

            html,
            body {
              width: 100%;
              height: 100%;
            }

            .container {
              display: flex;
              flex-flow: column;
              height: 100%;
              gap: 10px;
            }

            body>* {
              padding: 2rem;
              border: 5px solid white;
            }

            .col-2 {
              display: flex;
              gap: 10px;
              flex: 1;
            }

            .section {
              background: #eee;
              padding: 10px;
              flex: 1 50%;
            }

            .section__user {
              flex: 0
            }
        </style>

    </head>

    <body>
        <div class='container'>
            <div class='col-2'>
                <div class='section'>
                    <img src="hist.png" style="max-width: 100%;height: 100%">
                </div>
                <div class='section'>
                    <img src="amargan.png" style="max-width: 100%;height: 100%">
                </div>
            </div>

            <div class='col-2 section__user'>
                <div class='section'>user_enter_k</div>
            </div>

            <div class='col-2'>
                <div class='section'>
                    <img src="clustering.png" style="max-width: 100%;height: 100%">
                </div>
                <div class='section'>
                    <img src="scatter.png" style="max-width: 100%;height: 100%">
                </div>
            </div>
        </div>

    </body>
</html>
"""

with open("Golrang_AliAshja.html", "w") as file:
    file.write(htmlstring)
