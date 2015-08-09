# Google Calendar Particle Bridge

Streams the current event on all Google Calendar's associated with one account to any Particle device (Photon, Electron, etc.).

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
# put all environment variables from .secret on heroku
heroku config:set GOOGLE_REFRESH_TOKEN="xyz" GOOGLE_CLIENT_ID="xyz" GOOGLE_CLIENT_SECRET="xyz" PARTICLE_ACCESS_TOKEN="xyz"
heroku config:add TZ="America/New_York"
heroku ps:scale clock=1
```

-------------------------------------

## Creating Auth Credentials

The instructions on this url are fairly helpful for using curl to create an access/refresh token: https://developers.google.com/identity/protocols/OAuth2InstalledApp

For more detailed instructions, see below:

1. Go to https://console.developers.google.com and click Create Project. Give it a name and press ok.
2. After the project is created, go to "APIs & auth" on the left hand side and click "Consent Screen".
3. Change the "Product Name" and press save.
4. Now, go to "APIs & auth" on the left hand side and click "Credentials".
5. Click "Create new Client Id" and choose "Installed App". Under "Installed application type" choose other.
6. Copy the "Client Id" and "Client secret" into your .secret file.
7. Run the following command with your `client_id` and desired scope. This will return a "device_code", "user_code", and "verification_url".

    ```
    curl -d "client_id=<CLIENT_ID>&scope=https://www.googleapis.com/auth/calendar.readonly" https://accounts.google.com/o/oauth2/device/code
    ```

8. Tell the user to use his/her laptop to go to the verifiation url and type in the user code. This user will now be "forever" linked to this application.
9. To obtain the user's refresh token by run the following command with your `client_id`, `client_secret`, and `device_code`. This will return "access_token" and "refresh_token".

    ```
    curl -d "client_id=<CLIENT_ID>&client_secret=<CLIENT_SECRET>&code=<DEVICE_CODE>&grant_type=http://oauth.net/grant_type/device/1.0" https://www.googleapis.com/oauth2/v3/token
    ```

10. Take this refresh token and add it to the .secret file. Congragulations, you're done!

**NOTE**: to add a new user to the application, repeat steps 7-10 with the new user.

Bonus Step

To refresh the manually (the python code does this), run the following command with your `refresh_token`, `client_id`, and `client_secret`.

    curl -d "refresh_token=<REFRESH_TOKEN>&client_id=<CLIENT_ID>&client_secret=<CLIENT_SECRET>&grant_type=refresh_token" https://www.googleapis.com/oauth2/v3/token

