import boto3
import logging
from models.config import Settings

logger = logging.getLogger(__name__)

class SNSService:
    def __init__(self):
        settings = Settings()
        client_kwargs = {
            "region_name": settings.aws_region
        }
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        self.sns = boto3.client('sns', **client_kwargs)

    def send_sms(self, phone_number: str, message: str):
        """
        Sends an SMS message using AWS SNS.
        Ensures the number is in E.164 format.
        """
        try:
            # Clean and format phone number
            clean_number = "".join(filter(str.isdigit, phone_number))
            
            # If it's a 10-digit number, assume India (+91)
            if len(clean_number) == 10:
                e164_number = f"+91{clean_number}"
            elif not phone_number.startswith('+'):
                e164_number = f"+{clean_number}"
            else:
                e164_number = phone_number

            response = self.sns.publish(
                PhoneNumber=e164_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            logger.info(f"SMS sent successfully to {e164_number}", extra={"message_id": response.get('MessageId')})
            return response
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            return None
