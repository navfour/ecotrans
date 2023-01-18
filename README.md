# EcoForecast: An interpretable data-driven approach for short-term macroeconomic forecasting using N-BEATS neural network

We proposed an An interpretable Transformer-based large model for  macroeconomic forecasting that can support massive external multimodal data feeds

You can verify our model by real macroeconomic data in China, where you can open the related data in the`./data`.     The sample data contains "GDP" and uses "AAA" as external data.   You can choose the type of external data you want, and there is no limit to the amount of external data you can add.   Datasets are composed of three column fields, `Unique_ID` indicates the type of data, `ds` means the time,' y 'for data to be predicted, and 'exgenous' for external data.

ecotrans has proposed an extensible external data access method. After testing, with the increase of external data access quantity, our method has stronger robustness than the baseline method

You can watch the performance of the model change by adjusting the relevant parameters in 'GDPexample.py' and 'config_function_ex'. In 'GDPexample.py' we have rewrapped the hyperparameters of the model.

### Experiment

We compare the performance of A, B and C in economic forecasting. Compared with B and C, our model has significantly improved


![image](https://github.com/navfour/ecotrans/img1.svg)

![image](https://github.com/navfour/ecotrans/img2.svg)

### Datasets
The sample data covers 30 years from the first quarter of 1992 to the third quarter of 2022
## Usage
you can directly use `GDPexample.py` 

In "GDPexample.py", you can quickly compare the performance of EcoTrans in different structures and data sets by replacing the data sets we encapsulated the experiment in a different structure