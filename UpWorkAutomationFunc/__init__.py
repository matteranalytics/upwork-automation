import logging
from push_to_airtable import push_to_airtable
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Call your push_to_airtable function when the HTTP request is received
    try:
        push_to_airtable()
        message = "push_to_airtable function executed successfully. Alert email should be sent shortly"
        status_code = 200
    except Exception as e:
        logging.error(f"Error during the execution of push_to_airtable: {e}")
        message = "There was an error executing the push_to_airtable function."
        status_code = 500

    # Return a response
    return func.HttpResponse(
        message,
        status_code=status_code
    )

