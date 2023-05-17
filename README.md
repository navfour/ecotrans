# An interpretable Transformer-based framework for macroeconomic forecasting with massive external multimodal data

We propose EcoTrans, an open-source framework for macroeconomic forecasting with interpretability, using a
Transformer-based large model that unifies external data interface to support massive multimodal information access.

The `data` file is the example data, you can run it directly by running the `example.py` .You can choose the type of
external data you want, and there is no limit to the amount of external data you can add. Datasets are composed of three
column fields, `Unique_ID` indicates the type of data, `ds` means the time,`y` for data to be predicted, and `exgenous`
for external data.For more detailed data description you can refer to `readme` in the `Data` folder

It should be noted that what is given in the `example.py` file is the direct code of the experiment of the paper. In the
paper, circular cutting is adopted to cut the test set. You may not need to do this in a real application scenario. You
can remove some of the configuration loops from the `example.py` file, which we present in our new example
in `example2.py`.

You can watch the performance of the model change by adjusting the relevant parameters in `GDPexample.py`
and `config_function_ex.py`. It should be noted that our model supports long period prediction, but in our experiment
the prediction time is 1. This means that the results of all test sets need to be implemented through a loop. See the
comments in `GDPexample.py` for details

EcoTrans has proposed an extensible external data access method. After testing, with the increase of external data
access quantity, our method has stronger robustness than the baseline method, and the model also has a certain degree of
interpretability

### Experiment

We compared the performance of our model in different countries and across different types of data, and the overall
result was higher than the baseline model. In particular, from the results of the middle layer, our model can be well
fitted to the external data information. We have shown in the sample how to get the middle-tier results, which you can
do directly.

![image](https://github.com/navfour/ecotrans/blob/main/img/img1.svg)

table1 Ablation study over EcoTrans model’s performance on different countries

|     | China  | United States  | United Kindom | United Kindom |
|  ----  | ----  | ----  | ---- | ---- |
| N-BEATS (with no external data)   | 0.008103 | 0.004641  | 0.006511 | 0.004799 |
| EcoTrans (with no external data)  |0.006823|	0.033024|	0.006764|	0.004787|
| N-BEATSx (5 series)   |0.059242|	0.015212|	0.007450|	0.006196|
| EcoTrans (5 series)  |0.008331|	0.004304|	0.006784|	0.004936|
| N-BEATSx (10 series)  |0.058364|	0.011632|	0.007810|	0.004550|
| EcoTrans (10 series)  |0.007927|	0.004418|	0.006696|	0.004770|
| N-BEATSx (15 series)  |0.044965|	0.283166|	0.007845|	0.051633|
| EcoTrans (15 series)  |0.008460|	0.004237|	0.006805|	0.004810|
| N-BEATSx (20 series)  |0.050844|	0.228063|	0.008979|	0.022131|
| EcoTrans (20 series)  |0.008108|	0.004371|	0.006809|	0.005188|

Table The generalizability of EcoTrans for forecasting various macroeconomic indicators

|     | PMI  | Imports  | Exports | GR | PGO | CI | IE | Tax |
|  ----  | ----  | ----  | ---- | ---- | ---- | ---- | ---- | ---- |
|BVAR|0.0039|0.0161|0.0223|0.0352|0.0182|0.0324|0.0189 |0.0361|
|N-BEATS|0.0053|0.0235|0.0169|0.0651|0.0077|0.0128|0.0238 |0.0565|
|N-BEATSx|0.1594|0.0721|0.0691|0.0488|0.0074|0.0105|0.0232 |0.0591|
|EcoTrans |0.0030|0.0108|0.0222|0.0339|0.0065|0.0108|0.0208 |0.0420|




The numbers in the table represent the SMAPE error

![image](https://github.com/navfour/ecotrans/blob/main/img/img2.svg)

### Datasets

The sample data covers more than 30 years from the first quarter of 1990 to the third quarter of 2023.The external data used in
the experiment are shown in the table below, which are all from public data.

![image](https://github.com/navfour/ecotrans/blob/main/img/img_datainform.png)

### Usage

you can directly use `GDPexample.py`
