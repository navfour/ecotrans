import pandas as pd

from config_function import start

keyword = 'The_total_amount_of_export'
# Change data item
# len_test=['']
for i in ['2023_03', '2022_12', '2022_11', '2022_10', '2022_09', '2022_08', '2022_07', '2022_06',
          '2022_05', '2022_04', '2022_03']:
    # Change the length of test
    # Set the scope of the test set here and iterate through it
    Y_df = pd.read_csv('data/{}/{}_train{}.csv'.format(keyword, keyword, i), encoding='utf-8')
    Y_df2 = pd.read_csv('data/{}/{}_test{}.csv'.format(keyword, keyword, i), encoding='utf-8')
    # Test sets need to be implemented through multiple sets of data
    Y_df = Y_df.iloc[:, :3]
    Y_df2 = Y_df2.iloc[:, :3]
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
            result_df, result_predict = start(Y_df, Y_df2, windows_size, stack_types, n_blocks,
                                              string='{}{}'.format(keyword, i))
            ser = pd.DataFrame(result_predict.tolist(), columns=[str(nblock_name[0]) + '_' + str(windows_size)])
            result_end = result_end.join(ser, lsuffix='_block', rsuffix='_result')
            result_end.to_csv('result/{}/result_{}_{}.csv'.format(keyword, keyword, i))
            result_df.to_csv(
                'result/{}/result_{}_{}-block_{}.csv'.format(i, keyword, keyword,
                                                             str(nblock_name[0]) + '_' + str(windows_size)))
    # --------------------------------------------------------------
