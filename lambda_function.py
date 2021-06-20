import json
import boto3
# Importing "requests" library to make HTTPS calls to SP API endpoints
import requests
# Importing requests_aws4auth library to calculate the AWS SigV4 signature and add it to SP API requests
from requests_aws4auth.aws4auth import AWS4Auth


def lambda_handler(event, context):
    # Calling AssumeRole operation to receive temporary credentials from "SPAPIIAMRole" created through CloudFormation.
    client = boto3.client('sts')
    aws_account_id = context.invoked_function_arn.split(":")[4]
    iamrole = 'arn:aws:iam::'+aws_account_id+':role/SPAPIIAMRole'
    response = client.assume_role(
        RoleArn= iamrole,
        RoleSessionName='SPAPIRoleSession'
    )
    # Initializing AccessKey, SecretKey and SessionToken variables to be used in signature signing.
    AccessKeyId = response['Credentials']['AccessKeyId']
    SecretAccessKey = response['Credentials']['SecretAccessKey']
    SessionToken = response['Credentials']['SessionToken']
    
    # Fetch "client_id" and "client_secret" from your application in Seller Central by clicking on "View" in front of your application ID.
    client_id = 'your_application_client_id'
    client_secret = 'your_application_client__secret'

    # In order to call an API for a seller, you will need to paste the refresh_token for that particular seller below. 
    # Otherwise, you can self-authorize your application by clicking on "Authorize" from the dropdown menu in front of your application ID in seller central. 
    # Once you click on "Generate Refresh Token", you would be able to receive a refresh token and paste it below.
    refresh_token = 'paste_refresh_token_here'
    
    # Create body for calling "api.amazon.com/auth/o2/token" endpoint with grant_type as "refresh_token"
    payload = {'grant_type':'refresh_token','client_id':client_id,'client_secret':client_secret,'refresh_token':refresh_token}

    # Call the LWA endpoint to receive access token
    lwa = requests.post("https://api.amazon.com/auth/o2/token", data=payload)
    
    # Uncomment to print out the response of the LWA requests.
    #print(lwa.text)
    
    access_token = lwa.json()['access_token']
    
    # Create headers to add to SP API request. Headers should include: content_type and "x-amz-access-token"
    headers = {'content-type': 'application/json','Accept': 'application/json','x-amz-access-token':access_token}

    # Create AWS SigV4 signature with temporary credentials received from the above AssumeRole request.
    # AWS4Auth library calcuates the signature and creates a canonical string to be added in the "Authorization" header. It also adds x-amz-date and x-amz-security-token to the headers.
    auth = AWS4Auth(AccessKeyId, SecretAccessKey, 'us-east-1', 'execute-api',
                        session_token=SessionToken)

    # Add parameters for the GetOrders API test call
    params = {'CreatedAfter': '2020-01-19T03:58:30Z', 'MarketplaceIds': 'ATVPDKIKX0DER'}
    
    # Make a test call to the SP API Orders API endpoint with parameters, headers and AWS Signature Auth
    spapi = requests.get("https://sellingpartnerapi-na.amazon.com/orders/v0/orders", params=params, headers=headers, auth=auth)
    
    # Uncomment to print out the SP API request URL .
    #print("Request URL: ", spapi.request.url)

    # Uncomment to print out the Headers added to the request URL.
    #print("Request Headers: ", spapi.request.headers)
    
    print("Response: ", spapi.text)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
