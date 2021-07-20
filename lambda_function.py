import json
import boto3
from datetime import datetime, timedelta

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
    client_secret = 'your_application_client_secret'

    # In order to call an API for a seller, you will need to paste the refresh_token for that particular seller below. You can get refresh token for a seller using OAuth flow.
    # Otherwise, you can self-authorize your application by clicking on "Authorize" from the dropdown menu in front of your application ID in seller central. 
    # Once you click on "Generate Refresh Token", you would be able to receive a refresh token and paste it below.
    refresh_token = 'sellers_refresh_token'
    
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
    # If you want to call the EU or FE endpoint, change region in the parameters to "eu-west-1" or "us-west-2". For more information refer to this link: https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/developer-guide/SellingPartnerApiDeveloperGuide.md#selling-partner-api-endpoints
    auth = AWS4Auth(AccessKeyId, SecretAccessKey, 'us-east-1', 'execute-api',
                        session_token=SessionToken)
    
    # Make a call to the SP API Sellers API endpoint with headers and AWS Signature Auth
    # If you want to call the EU or FE endpoint, change the SP API endpoint to "sellingpartnerapi-eu" or "sellingpartnerapi-fe". For more information refer to this link: https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/developer-guide/SellingPartnerApiDeveloperGuide.md#selling-partner-api-endpoints
    sellersResponse = requests.get("https://sellingpartnerapi-na.amazon.com/sellers/v1/marketplaceParticipations", headers=headers, auth=auth)
    
    # Uncomment to print out the Sellers API request URL.
    #print("Request URL: ", sellersResponse.request.url)

    # Uncomment to print out the Headers added to the Sellers API request URL.
    #print("Request Headers: ", sellersResponse.request.headers)
    
    print("Seller participates in the following marketplaces: ", sellersResponse.text)
    
    # Fetch first marketplace Id from the list of supported marketplaces within the authorized region.
    marketplaceId = sellersResponse.json()['payload'][0]['marketplace']['id']
    
    # Get timestamp for 2 hours from now to fetch all orders within the last two hours
    createdAfter = (datetime.utcnow() - timedelta(hours=2)).isoformat()
    
    #print(createdAfter)
    
    # Add parameters for the GetOrders API call    
    params = {'CreatedAfter': createdAfter, 'MarketplaceIds': marketplaceId}
    
    # Make a call to the SP API Orders API endpoint with params, headers and AWS Signature Auth
    # If you want to call the EU or FE endpoint, change the SP API endpoint to "sellingpartnerapi-eu" or "sellingpartnerapi-fe". For more information refer to this link: https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/developer-guide/SellingPartnerApiDeveloperGuide.md#selling-partner-api-endpoints
    ordersResponse = requests.get("https://sellingpartnerapi-na.amazon.com/orders/v0/orders", params=params, headers=headers, auth=auth)
    
    # Uncomment to print out the Orders API request URL .
    #print("Request URL: ", ordersResponse.request.url)

    # Uncomment to print out the Headers added to the Orders API request URL.
    #print("Request Headers: ", ordersResponse.request.headers)
    
    print("Orders from the first Marketplace supported by seller: ", ordersResponse.text)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
