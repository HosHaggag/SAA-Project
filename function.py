import boto3
import os
from PIL import Image
from io import BytesIO

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key    = event['Records'][0]['s3']['object']['key']

    if key.startswith('saa/destination/'):
        return {"statusCode": 200, "body": "Skipping already processed image"}

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        image_content = response['Body'].read()

        img = Image.open(BytesIO(image_content))
        img = img.convert("RGB")
        img.thumbnail((100, 100))

        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)

        new_key = f"destination/{os.path.basename(key)}"

        s3.put_object(
            Bucket=bucket,
            Key=new_key,
            Body=buffer,
            ContentType='image/jpeg'
        )

        return {"statusCode": 200, "body": f"Image resized and saved to {new_key}"}

    except Exception as e:
        print(f"Error processing image: {e}")
        raise e