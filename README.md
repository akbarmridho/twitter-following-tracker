# Twitter Following Tracker

## How It Works
This script fetch user following list and save the result in MongoDB database. The following list will be updated every certain time interval. If there are difference between last and recent following list, it will send a notification to Telegram channel and update the spreadsheets.

## Prerequisites

1. Twitter Developer account.
2. MongoDB instance
3. Telegram API keys
4. Google Service Account.
5. Google Sheet API and Google Drive API enabled. Please refer to [This guide](https://support.google.com/googleapi/answer/6158841?hl=en) 

## Configuration

1. Twitter API keys including customer key, customer secret, bearer token, oauth access token, oauth access secret.
2. MongoDB instance. Example: `MONGODB_DB_HOST = mongodb+srv://<username>:<password>@cluster0.oynvk.mongodb.net/somedatabase` and `MONGODB_DB_NAME = somedatabase`.
3. Google Service Account. Please refer to [This guide](https://cloud.google.com/iam/docs/creating-managing-service-accounts#creating). Save downloaded service-account credentials into project folder as `google-credentials.json`.
4. Telegram API keys can be obtained from [Here](https://core.telegram.org/api/obtaining_api_id).
5. Prepare a sheet to save tracking result. Please make sure that your service account can access the file. Either make the sheet public and editable by everyone or give the service account email an access. Check the google-credentials.json and take service account email from client email field.
6. Prepare or create a public or private Telegram channel. Make sure you are an admin in that channel.
7. Create a comma separated list of Twitter username that want to be tracked. Example: `user1,user2,user3`.
8. Default check interval is 30 minutes. It is advised to set the interval higher if there are many account that are getting tracked. Don't make the interval lower as it could exceed Telegram API limits.

## Local Instalation

1. Open the script folder in your shell or bash.
2. Run `python install -r requirements.txt` or `python3 -r requirements.txt`.
3. Copy `.env.example` into `.env`. Fill the configuration data there.
3. Run `setup.py`. This script will initialize a Telegram session, configure target channel, and check for errors. Follow instruction carefully. Please include + sign when entering your Telegram phone number. Make sure that no error occured.
4. Run `app.py`.

## Heroku deployment

1. Create a Heroku project.
2. Clone the project git repository.
3. Copy this entire folder there.
4. Commit and push the changes.
5. Open project config vars. Fill each key and values to match `.env` file.
6. Restart the project.