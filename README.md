# Google Calendar SparkCore Bridge

Streams the current event on all Google Calendar's associated with one account to a SparkCore.

## Setup
```
pip install -r requirements.txt
cp .secret.example .secret
vim .secret # add necessary credentials in
source .secret
python clock.py
```

## Deploy

```
heroku ps:scale clock=1
```