import boto3

from django.conf import settings

SENDER_ID = 'CovidBeacon'
client = boto3.client('sns',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name='eu-west-1')


def send_sms(phone, msg):
    client.publish(PhoneNumber=phone,
                   Message=msg,
                   MessageAttributes={
                       'AWS.SNS.SMS.SenderID': {
                           'DataType': 'String',
                           'StringValue': SENDER_ID,
                        },
                       'AWS.SNS.SMS.SMSType': {
                           'DataType': 'String',
                           'StringValue': 'Transactional',
                        }
                    })
