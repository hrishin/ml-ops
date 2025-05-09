# Iris Classifier MLOps Project

An end-to-end MLOps implementation for the Iris flower classification model, 
demonstrating MLOps workflow for model training, serving using local envrionment 
and deploying the model through deployment pipeline.

## Project Overview

This project implements a simple machine learning pipeline for Iris flower classification 
with a focus on MLOps practices.

![Alt text](docs/images/1-model-serving.png)


## Pre-requisites

In order to run model training or deploy serving application locally,
please ensure the follow setup in insalled on the host

- python 3.12>=
- docker or podman
- make build 
- Kubectl
 - Helm

Before running any steps, plase ensure python virtual envionrment is initialized,
some setup is executed on the host

```bash
python -m venv venv && source venv/bin/activate
make setup
```


There are main loop developers or engineers would be following through the 
model SDLC(ML Ops)

 - Inner loop - Traing and test model locally, let iterate over model testing
 - Outer loop - Once model is ready to be deploy, developers would publish new 
 new model and deploy it through dev, staging and prod environment 

## Inner Loop

### Run model training

In order to run the model training, user could supply the sample
data through `./data/iris.csv` file. However do sample data 
provided system dump some sample data for common features 
of [Iris flower data sets](https://en.wikipedia.org/wiki/Iris_flower_data_set)

In order training model locally, execute

```bash
make training
......

Training ML model...
2025-05-08 17:12:47,887 - __main__ - INFO - Loading Iris dataset
2025-05-08 17:12:47,887 - __main__ - INFO - Loading data from data/iris.csv
2025-05-08 17:12:47,893 - __main__ - INFO - Building machine learning pipeline
2025-05-08 17:12:47,893 - __main__ - INFO - Training model...
2025-05-08 17:12:47,906 - __main__ - INFO - Model accuracy: 1.0000
2025-05-08 17:12:47,912 - __main__ - INFO - Classification report:
              precision    recall  f1-score   support

      setosa       1.00      1.00      1.00        10
  versicolor       1.00      1.00      1.00         9
   virginica       1.00      1.00      1.00        11

    accuracy                           1.00        30
   macro avg       1.00      1.00      1.00        30
weighted avg       1.00      1.00      1.00        30

2025-05-08 17:12:47,912 - __main__ - INFO - Saving model to artifacts/model_pipeline_1.0.20250508_171247.joblib
2025-05-08 17:12:47,913 - __main__ - INFO - Model training completed. Version: 1.0.20250508_171247
```
This training model store the training model under `artifacts` directory.

### Running model locally to test the model

In order to run the model locally, please execute

```bash
make run
```
This run the model serving service which serves some endpoints to 
test the model.

In order to test the model, either navigate to 
http://0.0.0.0:8000/docs#/default/predict_api_v1_predict_post
or run curl command, supply the sample input data

```json
//sample input for the test
{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2   
}
```

```bash 
curl -X POST http://0.0.0.0:8000/api/v1/predict \                                    
  -H "Content-Type: application/json" \
  -d '{ "sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2 }' \
| jq .
  
  
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   327  100   214  100   113  60847  32129 --:--:-- --:--:-- --:--:--  106k
{
  "prediction": 0,
  "prediction_label": "setosa",
  "request_id": "af12c702-4bfb-49d6-b877-d3635d8c9092",
  "model_version": "1.0.20250508_171813",
  "probabilities": [
    0.9790426981632894,
    0.020957142708309617,
    1.591284009687682E-7
  ]
}
```

### Running the intgration tests

In order to run automated integration tests on trained model, 
please executethe following command on pretrained 
model from the previous steps

```bash
make test
```

## Outer Loop

### Paackge and run container

Before start deploying the model, one can run the model serving
app as a container by following command

```bash
make build-run
```

### Build and publish model

Once ready to deploy the model, just create the tag using 
https://github.com/hrishin/ml-ops/actions/workflows/tag.yaml
github action.

This would allow user to either bump major, minor, patch or
user can pass the custom tag.

Essentially this automated workflow will tag the source 
latest commit on the main brnahc, build and publish the 
seving container image to the`docker.io/hrishi/ml-ops` 
repository.

At this moment this is how how the model version is maintained,
which represent the same tag.