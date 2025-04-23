# Bluebook_etl_lambda

----------------

This guide provides an overview of each ETL script located in the project and explains how to run them. Any newcomer can use this document to understand workflows at a glance.

## 1. Project Structure

1. The sharepointetl.py is responsible for managing the connection with the sharepoint folders, and downloading the files.
2. The main.py is the one responsible for coordinating all the project structure
3. The bluebook_etl is responsible for doing the transformations on the sharepoint excel file downloaded and updating the table on the database.

## 2. Environment setup

* There is a requirements.txt available. Start a virtual environment based on it.

## 3. Workflow

This repository is setup to be called through Lambda Function which is activated by its Lambda URL on the word file avaiable at LGG Guides documentation. 

The very beginning of this repository is at Bluebook Power Automate application that at its final steps creates the folders on sharepoint, uploads the excel file to it, and activates the Lambda Function through its url. 
