# EcoForecast: An interpretable data-driven approach for short-term macroeconomic forecasting using N-BEATS neural network

We proposed an interpretable data-driven approach for short-term macroeconomic forecasting named EcoForecast.

You can verify our model by real macroeconomic data in China, where you can open the related data in the`./data`. The dataset includes Gross Domestic Product (GDP) with a quarterly cycle, Purchasing Manager's Index (PMI) and National electricity generation (ELECT) with a monthly cycle. Datasets are composed of three column fields, `Unique_ID` indicates the type of data, `ds` means the time, and `y` indicates the value.

EcoForecast's interpretable decomposition result is consistent with the actual economics practice in China, which can analyze the dominant terms in economic change, providing intuition for further research.

You can observe the changes in model performance by manually tuning EcoForecast's block type and sliding window structures with configuration parameters in `GDPexample.py`, where we have rewrapped the model's hyperparameters.

##### Details can be found in this paper [https://www.sciencedirect.com/science/article/abs/pii/S0952197622002299].

### Experiment

We compare the performance of A, B and C in economic forecasting. Compared with B and C, our model has significantly improved


![image](https://github.com/navfour/ecotrans/img/img1.svg)

![image](https://github.com/navfour/ecotrans/img/img2.svg)

### Datasets
`GDP` data covers 30 years **from the first quarter of 1992 to the first quarter of 2022**, with 121 pieces updated quarterly. The `PMI` covers 17 years of data **from June 2005 to April 2022**, with 204 items updated monthly. `ELECT` covers 32 years of data **from June 1990 to March 2022**, with 375 updates monthly.

## Usage
you can directly use `GDPexample.py` or install the `ecoforecast` package

In `GDPexample.py`, you can quickly compare the performance of EcoForecast in different structures and different data sets by replacing datasets we had encapsulated experiments with different structures
