# HealthAI: TNM multi-centre dashboard

This repository contains the code for the HealthAI dashboard, which aims in 
demonstrating the potential of multi-centre analysis in a federated fashion. 
This dashboard showcases the feasibility of the federated approach using 
TNM data of non-small cell lung cancer patients. The data is distributed 
across five different Dutch hospitals: NKI, Isala, UMCG, Radboudumc and 
Maastro Clinic.

The project goal was to setup data nodes in each of the hospitals and 
investigate the feasibility of federated analysis for different data science 
typical tasks: simple statistics, supervised learning, and unsupervised 
learning. There has been numerous proof-of-concepts that shows the 
usefulness of federated analysis in the healthcare and other sectors. With 
this project, we show how to execute this approach in a real-life scenario 
and provide material that can be used as a template in any sector.

## Federated learning infrastructures

In this project we use two different federated learning infrastructures:
(Vantage6)[https://vantage6.ai/]
and (International Data Spaces - IDS)[https://tno-tsg.gitlab.io/docs/overview/].
Their documentation explains how to deploy the different infrastructures.

## Run dashboard

We assume that data nodes were deployed and that they hold TNM data of 
non-small cell lung cancer patients. In particular, a patient identifier (`id`), 
TNM stages (`t`, `n`, `m`), overall cancer stage (`stage`), diagnosis date 
(`date_of_diagnosis`), date of last follow-up (`date_of_fu`), and patient vital 
status (`vital_status`). If you have data nodes holding this type of data and 
following the same standard for the data content, you can run the dashboard 
with the following steps:

### Install the dependencies

We advise you to create a Python virtual environment using your favourite 
method and install the dependencies from the requirements list:

``` bash
pip install -r requirements.txt 
```

This code was developed and tested with Python 3.10.

### Run dashboard

You can run the dashboard by simply activating your virtual environment and 
then running the `index.py` script, an example of how to do it:

``` bash
source .venv/bin/activate 
python index.py
```

## Acknowledgments

This project was financially supported by the [AiNed foundation]
(https://ained.nl/over-ained/).
