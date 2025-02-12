# S&P500 Predictions Daily Report

This project generates daily predictions for the **S&P500** stock market index and sends a detailed report via email, including the full output and a graph visualization. The report is sent to a predefined mailing list, with the option to sign up for future reports.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup and Configuration](#setup-and-configuration)
  - [GitHub Secrets](#github-secrets)
- [Workflow](#workflow)
- [How to Contribute](#how-to-contribute)
- [License](#license)

## Overview

This project utilizes a **Python script** (`main.py`) to generate daily predictions for the **S&P500** stock index. It uses machine learning models and data analysis techniques to forecast market trends.

Once the predictions are made, the system sends a **daily email report** containing:

- A **summary of the prediction results**.
- A **graph** visualizing the predicted trends.
- A **full output file** for detailed information.

The email is sent to a set of recipients, including a **mailing list** stored as a GitHub secret, with an easy way to **sign up** for the mailing list.

## Sign Up for the Mailing List
Stay updated on the latest predictions and reports! Sign up for the mailing list to receive daily emails with the S&P500 predictions, including the output and visualizations.

[Sign Up for the Mailing List](https://docs.google.com/forms/d/e/1FAIpQLSdPx5574pl2MgkM1ipuvGwWduifqLDNS1vcLra0ConPeEtXPQ/viewform?usp=dialog)

Once you sign up, you'll receive an email with daily reports on the S&P500 predictions.


## Features

- **Daily Reports**: The system sends a daily email with the latest S&P500 predictions.
- **Attachments**: Each email contains a report file (`output.txt`) and a graph (`prediction_graph.png`).
- **BCC Recipients**: The mailing list is stored in GitHub secrets to maintain email privacy. The email is sent to all recipients via **BCC**.
- **Sign-Up Link**: Each email includes a link to sign up for the mailing list.
- **Automated Workflow**: The process is automated using GitHub Actions.

## Setup and Configuration

### GitHub Secrets

To run the workflow and send emails, you need to set up the following GitHub secrets:

1. **`EMAIL_USER`**: Your email address (e.g., `youremail@example.com`).
2. **`EMAIL_PASS`**: The app password or API key for your email account (e.g., for Gmail, use an app password).
3. **`EMAIL`**: The email address from which the reports will be sent.
4. **`MAILING_LIST`**: A comma-separated list of email addresses (e.g., `email1@example.com,email2@example.com`) for recipients in the BCC field.
5. **`API_KEY`**: If you're using an external service (e.g., for prediction or data collection), store the API key here.

You can add and update these secrets in the **GitHub repository settings** under **Settings > Secrets and variables > Actions**.

### Workflow Configuration

The workflow is defined in the `.github/workflows/scheduled-jobs.yml` file and runs automatically every day at 08:00 CEST.

1. The workflow runs the Python script (`main.py`) to generate predictions.
2. It generates and saves the graph and outputs.
3. It sends an email with attachments to the mailing list using **SMTP** and **Gmail** or any other supported email service.

### Adding Email Recipients

To update the **MAILING_LIST** (the list of email recipients), navigate to your GitHub repository **Settings > Secrets** and modify the `MAILING_LIST` secret. This will automatically update the recipients for the next email sent by the workflow.

## Workflow

- **Daily Run**: The workflow triggers every day at **08:00 CEST**.
- **Email Reports**: After generating the report and graph, the system sends an email with the following:
  - **Subject**: Includes the date and a brief description (e.g., `S&P500 Predictions Daily Report`).
  - **Body**: Includes a description of the report and the option to sign up for the mailing list.
  - **Attachments**: Contains `output.txt` and the prediction graph.

### How the Workflow Works:

1. The script is run automatically by the GitHub Actions scheduler.
2. The script performs data analysis, creates predictions, and saves output files.
3. The email is sent using Gmail (or another email service), with attachments included.
4. The recipients are added via BCC, keeping email addresses private.
5. The email includes a link to sign up for the mailing list.

## How to Contribute

Contributions are welcome! To get started:

1. Fork the repository.
2. Create a new branch.
3. Make your changes (e.g., add new features, improve scripts, etc.).
4. Create a pull request for review.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
