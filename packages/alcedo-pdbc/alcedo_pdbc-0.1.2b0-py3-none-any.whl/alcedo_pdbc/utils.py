# -*- encoding：utf-8 -*-

# ailab.pydc.utils
# Created :2024-8-10  9:33
# Author：AI Lab 100 Morgan
# Copyright (C) 2020-2024  数智教育发展 (山东) 有限公司
# For license information, see LICENSE.txt
# ID: utils.py


"""
`ailab.pydc.utils `模块包含了一些通用方法,具体如下:

- `which_dataframe` 用于检测返回的 `dataframe` 类型是 `Pandas`、`Polars` 还是 `Dask`
- `is_valid_config` 用于检测数据源的配置文件是否缺失参数
- `_df_to_file_writer` 用于将`dataframe`转成文件保存至本地

Nodes:
    `pip install tables`

    `pytables` 版本问题导致部分数据类型无法转换,需要手工添加.

    `nenv/Lib/site-packages/pandas/io/pytables.py` 修改 `_dtype_to_kind` 中添加数据类型,如 `Int64` 、`IntegerArray` 等.

    ``
    elif dtype_str.startswith(("int", "uint","Int64")):
        kind = "integer"
    elif dtype_str == "IntegerArray":
        kind = "integer"
    ``

"""

from pathlib import Path

from alcedo_pdbc.exceptions import ExtensionNotSupportException


def _which_dataframe(df):
    df_type = str(type(df)).split("'")[1]
    if df_type.startswith('pandas'):
        return 'pandas'
    elif df_type.startswith('polars'):
        return 'polars'
    elif df_type.startswith('dask'):
        return 'dask'


def _is_valid_config(config):
    required_keys = {'USERNAME','PASSWORD','HOST','PORT'}
    if not all(key in config and config[key] is not None for key in required_keys):
        raise ValueError("config缺少必要的参数,请重新输入.")
    else:
        return True


def _df_to_file_writer(df,filename: str) -> None:
    suffix = Path(filename).suffix
    # 判断后缀
    if suffix:
        extension = suffix[1:]
    else:
        extension = 'csv'
    # 根据后缀进行输出
    
    if extension == 'csv' and df is not None:
        df.to_csv(filename,index=False)
    elif extension == 'json' and df is not None:
        df.to_json(filename,orient='records')
    elif extension == 'xlsx' and df is not None:
        df.to_excel(filename)
    elif extension == 'xls' and df is not None:
        df.to_excel(filename)
    elif extension == 'html' and df is not None:
        df.to_html(filename)
    elif extension == 'h5' and df is not None:  # HDF5 文件
        df.to_hdf(filename,key='data',mode='w',format='table')
    elif extension == 'feather' and df is not None:  # HDF5 文件
        df.to_feather(filename)
    elif extension == 'parquet' and df is not None:  # Parquet 文件
        df.to_parquet(filename,index=False)
    else:
        raise ExtensionNotSupportException(f'无法识别/处理当前文件格式: {extension}')


if __name__ == '__main__':
    import pandas as pd
    
    df = pd.DataFrame({'Name':['Alice','Bob'],'Age':[25,30]})
    print(df.dtypes)
    df.to_csv("test.csv",index=False)