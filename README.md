# CovidBeacon

## API Endpoints

```
POST /auth/request_token
{
    'phone': …
}
```
Request an auth token, provided via SMS

```
POST /auth/login
{
    'phone': …, 
    'token': (token received via SMS)
}
```
Login with a token received via SMS. Returns a `sesssionId` cookie.

```
GET /api/user/profile
```
Get overview info of the current user, i.e. his estimated health status, recomennded actions and in-app permissions.

```
POST /api/user/profile
{
    data: {
        pushNotificationId: string,
    	lon: decimal,
        lat: decimal,
        locale: string,
    }
}
```
Provide information about the current user.

```
GET /api/user/contacts
```
Get a list of the current user's contacts with their estimated health status (if they've opted to share this information).

```
POST /api/user/contacts
{
    data: [ '+48123456789', ... ]
}
```
Provide a list of the current user contacts.

```
GET /api/questionnaire
```
Download the latest version of the in-app questionnaire.

```
POST /api/submission
{
    data: {
        result: [...]
    }
}
```
Submit an answer to the current version of the questionnaire as the current user.
