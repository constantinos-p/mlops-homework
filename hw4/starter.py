#!/usr/bin/env python
# coding: utf-8
import pickle
import pandas as pd
import argparse



with open('model.bin', 'rb') as f_in:
    dv, model = pickle.load(f_in)




categorical = ['PULocationID', 'DOLocationID']

def read_data(filename):
    df = pd.read_parquet(filename)
    
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df


# In[22]:


def predict_result(year,month):
    df = read_data(f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet')
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)
    print(f'mean prediction {y_pred.mean()}')
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    predictionDf = pd.DataFrame(y_pred, columns=['prediction'])
    df_result = pd.concat([df['ride_id'], predictionDf], axis=1)

    df_result.to_parquet(
        'result.parquet',
        engine='pyarrow',
        compression=None,
        index=False
    )

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Predict taxi ride durations.')
    parser.add_argument('--year', type=int, required=True, help='Year of the data to process')
    parser.add_argument('--month', type=int, required=True, help='Month of the data to process')

    # Parse arguments
    args = parser.parse_args()

    # Call the main function with parsed arguments
    predict_result(args.year, args.month)





