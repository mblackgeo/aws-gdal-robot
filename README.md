# AWS GDAL Robot
A proof of concept implementation of running GDAL based jobs in AWS

Structure:
* A GDAL/rasterio container based job that converts an S3 object to a Cloud Optimised GeoTiff
* An AWS Lambda function that will trigger the above container to run in AWS Batch
* CDK constructs for configuration of S3, Lambda, Batch, etc.