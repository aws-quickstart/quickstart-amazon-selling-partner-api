
---
global:
  marketplace-ami: false
  owner: quickstart-eng@amazon.com
  qsname: quickstart-amazon-selling-partner-api
  regions:
    - ap-northeast-1
    - ap-northeast-2
    - ap-southeast-1
    - ap-southeast-2
    - eu-central-1
    - eu-west-1
    - sa-east-1
    - us-east-1
    - us-west-1
    - us-west-2
  reporting: true

tests:
  quickstart-amazon-selling-partner-apit1:
    parameter_input: quickstart-amazon-selling-partner-api-example-params1.json
    template_file: quickstart-amazon-selling-partner-api-example1.template
  quickstart-amazon-selling-partner-apit2:
    parameter_input: quickstart-amazon-selling-partner-api-example-params2.json
    template_file: quickstart-amazon-selling-partner-api-example2.template