provider "aws" {
    region = "us-east-1" 
    access_key = var.aws_access_key
    secret_key = var.aws_secret_key
   
}

variable "aws_access_key" {
    description = "AWS Access Key"
    type = string
    default = "value"
    }

variable "aws_secret_access_key" {
    description = "AWS Secret Access Key"
    type = string
    default = "value"
    }
#In the case, the enviroment is dev, since we´re doing a test. But it could be test or prod
variable "environment" {
    description = "Environment"
    type = string
    default = "dev"
    }

variable "project_name" {
    description = "Reddit_airflow"
    type = string
    default = "data-pipeline"
    }