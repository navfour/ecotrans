import pandas as pd

from config_function_ex import start

for i in ['2022_Q3']:
    Y_df = pd.read_csv('data/人民币美元汇率/GDP_train{}.csv'.format(i), encoding='utf-8')
    Y_df2 = pd.read_csv('data/人民币美元汇率/GDP_test{}.csv'.format(i), encoding='utf-8')


    result_end = Y_df2.drop(index=[0])
    result_end.reset_index(drop=True, inplace=True)

    # -------验证STG的结构
    # STG,SGT,TGS,TSG,GTS,GST,STGG,TSGG

    dict_n_blocks = [
        [['seasonality'] + ['trend'] + ['identity'], [1, 1, 5], ['STGI']],
        #         [['seasonality'] + ['identity'] + ['trend'], [1, 5, 1], ['SGT']],
        #         [['trend'] + ['identity'] + ['seasonality'], [1, 5, 1], ['TGS']],
        #         [['trend'] + ['seasonality'] + ['identity'], [1, 1, 5], ['TSG']],
        #         [['identity'] + ['trend'] + ['seasonality'], [5, 1, 1], ['GTS']],
        #         [['identity'] + ['seasonality'] + ['trend'], [5, 1, 1], ['GST']],
        #         [['seasonality'] + ['trend'] + ['identity'], [1, 1, 20], ['STGG']],
        #         [['trend'] + ['seasonality'] + ['identity'], [1, 1, 20], ['TSGG']],
    ]
    windows_sizes = [12]

    for blok_stack in dict_n_blocks:
        stack_types = blok_stack[0]
        n_blocks = blok_stack[1]
        nblock_name = blok_stack[2]
        for windows_size in windows_sizes:
            result_df, result_predict = start(Y_df, Y_df2, windows_size, stack_types, n_blocks, string='人民币美元汇率')
            ser = pd.DataFrame(result_predict.tolist(), columns=[str(nblock_name[0]) + '_' + str(windows_size)])
            result_end = result_end.join(ser, lsuffix='_block', rsuffix='_result')
            result_end.to_csv('result测试集/result人民币美元汇率/result-GDP_{}.csv'.format(i))
            # result_df.to_csv('resultss/result-GDP22-block_{}.csv'.format(str(nblock_name[0]) + '_' + str(windows_size)))
    # --------------------------------------------------------------
