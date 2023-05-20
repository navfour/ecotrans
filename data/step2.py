import pandas as pd
import numpy as np
import os

# list_df = [
#     'df_发电.xlsx',
#     'df_工业企业.xlsx',
#     'df_工业增加值.xlsx',
#     'df_房地产.xlsx',
#     'df_税收.xlsx',
#     'df_财政.xlsx',
#     'df_零售.xlsx',
# ]
# filename_list = [
#     'fadian',
#     'gongye_qiye',
#     'gongye_zengjia',
#     'fang',
#     'shui',
#     'cai_zheng',
#     'lingshou',
# ]
list_df = [
    'data.xlsx',
]
filename_list = [
    'gongye_zengjia',
]
time_list = ['2023_03', '2022_12', '2022_11', '2022_10', '2022_09', '2022_08', '2022_07', '2022_06',
             '2022_05', '2022_04', '2022_03']
for xlsx_name, file_name in zip(list_df, filename_list):

    if not os.path.exists('result_bvar/{}'.format(file_name)):
        os.mkdir('result_bvar/{}'.format(file_name))
    df = pd.read_excel('data/{}'.format(xlsx_name))
    # print(df)
    df = df.fillna(value=0, method=None, axis=None, inplace=False)
    df = df.iloc[:, 0:33]
    # print(df)
    num = 0
    for i in time_list:
        df.to_csv('0512/{}/{}_test{}.csv'.format(file_name, file_name, i), index=None, encoding='utf-8')
        df = df.iloc[:-1]
        # print(df)
        df.to_csv('0512/{}/{}_train{}.csv'.format(file_name, file_name, i), index=None, encoding='utf-8')
        num = num + 1
