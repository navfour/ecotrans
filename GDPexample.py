import pandas as pd

from config_function_ex import start

for i in ['2022_Q3']:
#Set the scope of the test set here and iterate through it
    Y_df = pd.read_csv('data/USDCNY/GDP_train{}.csv'.format(i), encoding='utf-8')
    Y_df2 = pd.read_csv('data/USDCNY/GDP_test{}.csv'.format(i), encoding='utf-8')
#Test sets need to be implemented through multiple sets of data

    result_end = Y_df2.drop(index=[0])
    result_end.reset_index(drop=True, inplace=True)

    dict_n_blocks = [
        [['seasonality'] + ['trend'] + ['identity'], [1, 1, 5], ['STGI']]        
    ]
    windows_sizes = [12]
# change the “windows_size” 、“stack strategy”
    for blok_stack in dict_n_blocks:
        stack_types = blok_stack[0]
        n_blocks = blok_stack[1]
        nblock_name = blok_stack[2]
        for windows_size in windows_sizes:
            result_df, result_predict = start(Y_df, Y_df2, windows_size, stack_types, n_blocks, string='USDCNY')
            ser = pd.DataFrame(result_predict.tolist(), columns=[str(nblock_name[0]) + '_' + str(windows_size)])
            result_end = result_end.join(ser, lsuffix='_block', rsuffix='_result')
            result_end.to_csv('results/result-GDP_{}.csv'.format(i))
    # --------------------------------------------------------------
