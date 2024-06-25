# Overview
A data violation reporting system, implemented using Python and FastAPI. Incoming reports are validated and converted into emails.

Example request:
```json
{
    "title": "Personally Identifiable Information Issue",
    "description": "There are various examples of personal details in the Aurora Articles dataset.",
    "report_type": "data_violation",
    "category": "personal_data",
    "dataset_id": "fake_aurora_dataset_id",
    "examples": [
        {
            "data_id": "fake_aurora_data_id_0",
            "description": "Contains reference to phone numbers",
        },
        {"data_id": "fake_aurora_data_id_1"},
    ],
}
```

Resulting email:
```
Recipient: info@auroraarticles.com
Title: [Data Violation Alert] Report received for dataset 'Aurora Articles Catalogue': 'Personally Identifiable Information Issue'
Body:

A data violation issue has been reported.

Reporter: Oscar Chen - Blog Bot (ochen@blogbot.com)
Category: personal_data
Dataset: Aurora Articles Catalogue
Description:
There are various examples of personal details in the Aurora Articles dataset.
    
Examples:
    - (fake_aurora_data_id_0): Contains reference to phone numbers
    - (fake_aurora_data_id_1): No description
```

# Assumptions
- All email addresses are up to date in the database. Since there is no persistence, a report is lost if it is sent to the wrong email address.
- It is okay to send the reporter email address to the publisher. This allows the publisher to ask the reporter clarifying questions on the report.
- There is no need to automatically action (e.g. hide/delete) any data violation report - would have to confirm with legal.
- There is no need to automatically notify other organisations licensed for the violating dataset. They would be manually alerted after the report is confirmed.
- This service is not frequently called. There is currently no rate limiting, and a issue on the reporter side could cause a publishing company to be spammed with emails.

# Code Walkthrough
- `main.py` - Provides the entrypoint, and is responsible for overriding the database and email clients to use
the fakes provided in `app/fakes/fake_db.py` and `app/fakes/fake_email.py`.
- `routers/report.py` - Implements the endpoint handler for clients sending report requests. It takes advantage of the
[FastAPI dependencies system](https://fastapi.tiangolo.com/tutorial/dependencies/) to authenticate the reporter, check
the provided dataset ID/data ID is in the database, and check the reporter is permissioned for this dataset. This report
is converted into human readable text before being sent to the email client.
- `app.py` - Creates the FastAPI app and links in the report router.
- `db.py` - (Unimplemented) database client.
- `email.py` - (Unimplemented) email client.
- `models.py` - Models for data objects stored in database.
- `token.py` - Provides the dependency required to verify the token in incoming requests.
- `users.py` - Provides the dependency required to extract a user from a token. 

# Instructions
Set up a virtualenv and install dependencies:
```bash
python3.12 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

The service can now be started with:
```bash
python main.py
```
By default, requests can be interactively sent to the service at http://localhost:8000/docs. Requests must be sent with the token "dummy_token" to be authenticated.

Unit tests can be run with:
```bash
pytest
```

# Further Improvements
- Rather than sending an email on each report request, this service should instead be integrated into some third party issues tracking solution. This would enhance the reporting experience with many important features:
    - Persistent tracking of open issues.
    - Tracking the time elapsed since the report, which may be essential if certain regulators require action within a certain timeframe.
    - Ability for the publisher/reporter/Human Native AI to ask clarifying questions/provide further supporting information.
    - Allows multiple people from the reporting/publishing organisation to view the open issues, rather than relying on people forwarding emails.
    - Editing after the report is sent.
    - Attaching supporting evidence in other formats.
    - Filtering by severity - certain data violations are higher priority than others.
    - Can link other organisations who are licensed for the violating dataset. This would allow others to be aware of a potential problem, track its progress, and provide supporting evidence.
- Some data violations are higher priority than others (e.g. special category data). A severity level should be calculated based on the report details.
- For video, animation and audio data types, it might be helpful to enforce the reporter to input timestamp fields.
