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
[Vantage6](https://vantage6.ai/) and 
[International Data Spaces - IDS](https://tno-tsg.gitlab.io/docs/overview/).
Their documentations explain how to deploy the different infrastructures.

## Input data

We assume that data nodes were deployed and that they hold TNM data of
non-small cell lung cancer patients. In particular, a patient identifier (`id`),
TNM stages (`t`, `n`, `m`), overall cancer stage (`stage`), diagnosis date
(`date_of_diagnosis`), date of last follow-up (`date_of_fu`), and patient vital
status (`vital_status`). The data should follow the common data model 
described in the `cdm.json` file in the `input` directory.

## Run dashboard

You can run the dashboard either locally or using the docker image. Below 
you can see the required steps for each case.

### Run with docker

You can run the dashboard with docker. Firstly, you need to 
create and edit a `config.py` file with the appropriate input for the 
vantage6 user client and the tasks. Please see an example located at 
`pages/config_example.py`. After that, you can simply run the following 
docker command to start the dashboard:

``` bash
docker run --rm -d \
    --name healthai-dashboard \
    -p 5000:5000 \
    -v $(pwd)/config.py:/pages/config.py:ro \
    ghcr.io/maastrichtu-cds/healthai-dashboard:latest
```

### Run locally

#### Install the dependencies

We advise you to create a Python virtual environment, using your favourite 
method, and install the dependencies from the requirements list:

``` bash
pip install -r requirements.txt 
cp pages/config_example.py pages/config.py
```

Notice that you need to edit the `config.py` file with the appropriate input
for the vantage6 user client and the tasks. 
This code was developed and tested with Python 3.10.

#### Run dashboard

You can run the dashboard by simply activating your virtual environment and 
then running the `index.py` script, an example of how to do it:

``` bash
source .venv/bin/activate 
python index.py
```

## Acknowledgments

This project was financially supported by the 
[AiNed foundation](https://ained.nl/over-ained/).
