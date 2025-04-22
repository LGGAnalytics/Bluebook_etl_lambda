import logging
from datetime import datetime
from main import run_bluebook_menu

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda entry point for SharePoint ETL tasks.

    Args:
        event (dict): AWS Lambda event data.
        context (object): AWS Lambda context object.

    Returns:
        dict: HTTP-style response indicating success or failure.
    """
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            },
            "body": "OK"
        }
    
    try:
        logger.info("Starting menu ETL process...")
        run_bluebook_menu()
        
        logger.info("Blubebook ETL process complete.")
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            },
            "body": "Success"
        }
    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            },
            "body": f"Failure: {str(e)}"
        }