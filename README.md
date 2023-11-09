# Upwork Automation

This repository contains a Python script designed to scrape job postings from Upwork and an Azure Function that controls the automation process.

## Python Script

The main Python script (`parser_script.py`) performs the following actions:

- Fetches job postings from Upwork RSS feeds based on specified queries.
- Parses the job posting details using `feedparser` and `BeautifulSoup`.
- Processes and cleans the data with `pandas`.
- Pushes the new job postings to an Airtable database using `pyairtable`.
- Sends notification emails upon completion or if an error occurs.

## Azure Function

The Azure Function (`__init__.py`) is set up to trigger the automation process:

- It is triggered by an HTTP request.
- Executes the `push_to_airtable` function from the Python script.
- Sends an HTTP response indicating the success or failure of the operation.

## Setup and Deployment

1. Clone the repository.
2. Install the required Python packages.
3. Configure the necessary environment variables for email and Airtable access.
4. Deploy the Azure Function to your Azure account.
5. Set up an HTTP trigger to initiate the `push_to_airtable` function.

## Contribution

This project is maintained by Matter Analytics. We value contributions from the community. To contribute:

1. Fork the repository.
2. Make your changes and write clear, concise commit messages.
3. Submit a pull request with a description of your changes.

All contributions are subject to approval by Matter Analytics.

## License

This project and repository are owned by Matter Analytics. All rights reserved. The code is proprietary and may not be used or distributed without explicit permission from Matter Analytics.
