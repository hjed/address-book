A very simple address book program by Harry J.E Day for Google Appengine

# Dependencies

please run `npm install` to install all dependencies.

# Deployment

run: `gcloud --project=your-app app deploy app.yaml`

# Files

- index.html - contains a basic interface for the rest api, using html and angular
- main.py - request handlers for the api
- address_data.py - the ndb model and helper functions
- app.yaml - the config file for appengine