# OAuth 2.1 and OpenID Connect

Let users sign in with Google and call Google APIs with their token. The examples need your own Google OAuth client ID and secret.

## Key points

- OAuth delegates authorization; OpenID Connect adds identity through the ID token.
- OAuth 2.1 keeps the authorization code flow with PKCE and drops the implicit and password grants.
- Register the redirect URI `{baseUrl}/login/oauth2/code/{registrationId}` exactly as the app will send it.
- `oauth2Login()` handles the redirect, code exchange, and ID token validation; the user becomes an `OidcUser`.
- `OAuth2ClientHttpRequestInterceptor` puts the user's access token on `RestClient` calls.

## Example

Add `spring-boot-starter-security-oauth2-client`. Configure the [Google registration](#13_Spring_Boot/18_OAuth_2.1_and_OpenID_Connect/concepts/register-a-google-client), [login chain](#13_Spring_Boot/18_OAuth_2.1_and_OpenID_Connect/concepts/sign-in-with-oauth2login), and [`/me` endpoint](#13_Spring_Boot/18_OAuth_2.1_and_OpenID_Connect/concepts/oauth-2-0-and-openid-connect). Start the app, then open `http://localhost:8080/me` in a browser.

```sh
export GOOGLE_CLIENT_ID=your-client-id GOOGLE_CLIENT_SECRET=your-secret
./mvnw spring-boot:run
```
