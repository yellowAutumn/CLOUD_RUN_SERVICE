# main.py
import functions_framework # Required for Cloud Functions
import requests            # Used for making HTTP requests
import os                  # Used for reading environment variables
import json                # Used for formatting the output as JSON

@functions_framework.http
def test_internal_lb(request):
    """
    HTTP Cloud Function that calls an internal HTTP(S) Load Balancer
    and returns its response.

    Args:
        request (flask.Request): The incoming HTTP request object to this Cloud Function.

    Returns:
        A JSON response containing the status of the call to the Load Balancer,
        including its status code and body.
    """

    # --- Configuration from Environment Variables ---
    # Retrieve the Load Balancer's internal IP address from an environment variable.
    # IMPORTANT: You MUST set this environment variable (e.g., LOAD_BALANCER_IP=http://10.0.0.5)
    # when deploying this Cloud Function.
    load_balancer_ip = os.environ.get("LOAD_BALANCER_IP")

    # Retrieve the target path that your backend service (Cloud Run) expects.
    # Defaulting to "/" if not provided.
    target_path = os.environ.get("TARGET_PATH", "/")
    # --- End Configuration ---

    # --- Input Validation ---
    if not load_balancer_ip:
        error_message = "Error: LOAD_BALANCER_IP environment variable is not set. Please provide the internal IP of your load balancer (e.g., http://10.0.0.5)."
        print(error_message) # Print to Cloud Function logs for debugging
        response_data = {"status": "error", "message": error_message}
        # Return a JSON response with a 500 status code
        return json.dumps(response_data), 500, {'Content-Type': 'application/json'}
    # --- End Input Validation ---

    # --- Call the Internal Load Balancer ---
    try:
        # Construct the full URL for the internal Load Balancer
        internal_url = f"{load_balancer_ip}{target_path}"
        print(f"Attempting to call internal Load Balancer at: {internal_url}") # Log the attempt

        # Make the HTTP GET request.
        # This Cloud Function MUST be configured with Serverless VPC Access to your VPC
        # for this internal call to succeed.
        response = requests.get(internal_url, timeout=15) # Set a timeout to prevent hanging

        # Raise an HTTPError for bad responses (4xx or 5xx status codes)
        response.raise_for_status()

        # If successful, prepare the structured JSON response
        response_data = {
            "status": "success",
            "message": "Successfully called internal Load Balancer.",
            "called_url": internal_url,
            "load_balancer_response_status_code": response.status_code,
            "load_balancer_response_headers": dict(response.headers), # Convert headers to a dictionary
            "load_balancer_response_body": response.text # Get the text content of the response
        }
        # Return a JSON response with a 200 status code
        return json.dumps(response_data), 200, {'Content-Type': 'application/json'}

    # --- Error Handling for Network Issues ---
    except requests.exceptions.Timeout:
        error_message = f"Timeout error: Request to Load Balancer at {internal_url} timed out after 15 seconds."
        print(error_message)
        response_data = {"status": "error", "message": error_message}
        # Return a JSON response with a 504 status code (Gateway Timeout)
        return json.dumps(response_data), 504, {'Content-Type': 'application/json'}

    except requests.exceptions.ConnectionError as e:
        error_message = f"Connection error: Could not connect to Load Balancer at {internal_url}. This often indicates a networking issue (VPC Access configuration, firewall rules, or incorrect LB IP). Error details: {e}"
        print(error_message)
        response_data = {"status": "error", "message": error_message}
        # Return a JSON response with a 503 status code (Service Unavailable)
        return json.dumps(response_data), 503, {'Content-Type': 'application/json'}

    except requests.exceptions.RequestException as e:
        # Catch any other requests-related errors (e.g., HTTP status errors from raise_for_status)
        error_message = f"HTTP Request error: An error occurred while making the request to {internal_url}. Error details: {e}"
        print(error_message)
        response_data = {"status": "error", "message": error_message}
        # Return a JSON response with a 500 status code (Internal Server Error)
        return json.dumps(response_data), 500, {'Content-Type': 'application/json'}

    except Exception as e:
        # Catch any other unexpected errors
        error_message = f"An unexpected error occurred in the Cloud Function: {e}"
        print(error_message)
        response_data = {"status": "error", "message": error_message}
        # Return a JSON response with a 500 status code (Internal Server Error)
        return json.dumps(response_data), 500, {'Content-Type': 'application/json'}

