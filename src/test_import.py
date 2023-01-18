from src import test_getdata
import pandas as pd
import numpy as np


def nothing():
    df = pd.read_csv('data/GDP人民币美元汇率.csv', index_col=None, header=None)
    df_numpy = np.array(df)
    data_df = pd.DataFrame(df_numpy)

    aaa, bbb = test_getdata.getx_t(data_df)
    print(aaa)
    print(bbb)
