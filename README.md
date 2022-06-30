# AWS GDAL Robot
A proof of concept implementation of triggering GDAL based jobs in AWS Batch based on files being upload to S3.

This proof of concept will convert a tiff image uploaded to S3 into a [Cloud Optimised Geotiff](https://www.cogeo.org/). There are many things not covered in this proof of concept (see TODO below), but it is intended to be a rough demo for how to trigger AWS Batch from S3 event notifications via AWS Lambda. An alternative approach, which is perhaps a better option, would be to use EventBridge to trigger Batch, which would remove the need for the Lambda step in between. 

Structure:
* [`convert`](convert/) - A GDAL/rasterio container based job that converts an S3 object to a Cloud Optimised GeoTiff
* [`lambda`](lambda/) - An AWS Lambda function that will trigger the above container to run in AWS Batch
* [`deploy`](deploy/) - CDK constructs for configuration of S3, Lambda, Batch, and some monitoring with SNS

![AWS Diagram](diagram.png)

When a (tif/tiff) file is uploaded to the created "input" S3 bucket, it triggers an S3 notification that runs the Lambda function. The Lambda function in turn then triggers AWS Batch to run the `convert` container job that will output a COG to the "output" S3 bucket.

# TODO

- [x] Separate input/output buckets
- [ ] Human readable bucket names
- [ ] Bucket deletion policies
- [ ] Enable bucket versioning to ensure S3 events are always triggered
- [x] Basic filtering so it only triggers on tif/tiff files
- [x] SNS notifications if batch job fails
- [ ] Nicer human readable notifications for failures
- [ ] Use CloudTrail/EventBridge to trigger Batch instead of s3 bucket notifications (can probably remove lambda step)
