# EcoTrans: An interpretable large-scale Transformer-based model for macroeconomic forecasting with massive external multimodal data
We propose EcoTrans, an open-source framework for macroeconomic forecasting with interpretability, using a Transformer-based large model that unifies external data interface to support massive multimodal information access.

The `.data/USDCNY` file is the example data, you can run it directly by running the `XXX.py` file.You can choose the type of external data you want, and there is no limit to the amount of external data you can add.   Datasets are composed of three column fields, `Unique_ID` indicates the type of data, `ds` means the time,`y` for data to be predicted, and `exgenous` for external data.

EcoTrans has proposed an extensible external data access method. After testing, with the increase of external data access quantity, our method has stronger robustness than the baseline method, and the model also has a certain degree of interpretability

You can watch the performance of the model change by adjusting the relevant parameters in `GDPexample.py` and `config_function_ex`. It should be noted that our model supports long period prediction, but in our experiment the prediction time is 1. This means that the results of all test sets need to be implemented through a loop. See the comments in `XXX.py` for details

### Experiment

Compared with the baseline method, our method has a significant improvement. Compared with the baseline method, our method has a significant improvement. With the increase of external data, our model becomes more robust.

![image](https://github.com/navfour/ecotrans/blob/main/img/img1.svg)

![image](https://github.com/navfour/ecotrans/blob/main/img/img2.svg)

### Datasets
The sample data covers 30 years from the first quarter of 1992 to the third quarter of 2022

### Usage
you can directly use `GDPexample.py`
