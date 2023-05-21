# Dataset Introduction

### Introduction
We provide experimental data, raw data and data preprocessing code

experimental data contains all the experimental data, Including 'China_GDP', 'Chinese_Tax_Revenue', 'Completed_Investment_in_Real_Estate_Development', 'Germany_GDP', 'Goverment_Revenue', ‘Japan_GDP‘,‘PMI‘,‘Power_Generation_Output‘,‘The_total_amount_of_export‘,‘The_total_amount_of_import‘,‘Total_Profit_of_I ndustrial_Enterprises‘,‘UK_GDP‘,‘US_GDP‘


### Special Instructions
Our model can support long period prediction, but in this experiment, only 1 is selected as the prediction step parameter. Therefore, we need to cut each set of experimental data into several independent experiments. For example, if the length of the test set is 2019Q1-2022Q4, we need to cut three years times four quarters, a total of 12 independent experiments. The specific preprocessing method is given in "step2.py", and the processing results are in the "Experimental data" folder. If you just want to reproduce the experimental results of the paper, you can run it directly

### Data Item
Our data are mainly divided into two categories. One group is the GDP data of various countries and relevant external data, including the US, the UK, China and Japan. The other group is China's "PMI", "The total amount of import, billion USD/month "," The total amount of export, billion USD/month”,“Goverment Revenue, billion RMB/month”,“Power Generation Output,  billion kWh/month”,“Completed Investment in Real Estate Development,  billion USD/month”,“Total Profit of Industrial Enterprises, billion USD/month”,“Tax Revenue,  billion RMB/month "eight macro data and related external data. Specific data items are shown in the following table (under improvement......)


|     | China  | United States  | United Kindom | Japan |
|  ----  | ----  | ----  | ---- | ---- |
|  ----  | ----  | ----  | ---- | ---- |
|  ----  | ----  | ----  | ---- | ---- |
|  ----  | ----  | ----  | ---- | ---- |
|  ----  | ----  | ----  | ---- | ---- |
|  ----  | ----  | ----  | ---- | ---- |


|     | PMI  | Imports  | Exports | GR | PGO | CI | IE | Tax |
|  ----  | ----  | ----  | ---- | ---- | ---- | ---- | ---- | ---- |
|  ----  | ----  | ----  | ---- | ---- | ---- | ---- | ---- | ---- |
|  ----  | ----  | ----  | ---- | ---- | ---- | ---- | ---- | ---- |
|  ----  | ----  | ----  | ---- | ---- | ---- | ---- | ---- | ---- |
|  ----  | ----  | ----  | ---- | ---- | ---- | ---- | ---- | ---- |
|  ----  | ----  | ----  | ---- | ---- | ---- | ---- | ---- | ---- |
|  ----  | ----  | ----  | ---- | ---- | ---- | ---- | ---- | ---- |

### Data Preprocessing

Our external data is taken from the heat ranking of commercial databases, and there are more than 100 alternative external data. We will eliminate too much difference between the start time and the end time (indicators that are more than ten years, that is, the statistics did not start before 2000) and the data that are too correlated with the predicted data (for example, in the forecast of GDP indicators, we will eliminate the GDP growth rate, the GDP value of the primary industry and other derivative data). Original data In the "original data" folder, data preprocessing includes two py files, which are respectively to remove invalid external data and to cut data into several groups of independent experimental data.