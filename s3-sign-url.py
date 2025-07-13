import boto3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


s3 = boto3.client('s3')

def lambda_handler(event, context):
    # key = 'output/' + event['file_name']  # your processed image path
    key    = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']

    clean_key = key.replace("%40", "@")

    print(f"Processing file: {clean_key} from bucket: {bucket}")

    
    # Generate signed URL
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': clean_key},
        ExpiresIn=300  # URL expires in 5 minutes
    )

    print(f"Generated signed URL: {url}")

    if not url:
        return {
            "statusCode": 500,
            "body": "Failed to generate signed URL"
        }


    GMAIL_USER = "haggagdev@gmail.com"
    GMAIL_PASS = "*************"

    to_email =  clean_key.split('/')[-1]  # Extract the filename from the key
    subject = "Image Processed Successfully"
    body =  "Your image has been processed successfully. You can download it from the following link: " + url

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = GMAIL_USER
    msg['To'] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, [to_email], msg.as_string())
        server.quit()

        print(f"Email sent successfully to {to_email}")

        return {
            "statusCode": 200,
            "body": f"Email sent successfully to {to_email}"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }