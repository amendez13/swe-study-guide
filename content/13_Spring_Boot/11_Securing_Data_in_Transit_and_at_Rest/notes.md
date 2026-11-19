# Securing Data in Transit and at Rest

Protect data on the wire with TLS through SSL bundles, and protect stored data with hashing and column encryption.

## Key points

- An SSL bundle names TLS material once; the server and clients refer to it by name.
- `reload-on-update` picks up rotated certificates without a restart.
- Scope trust for a private CA to the client that needs it with `RestClientSsl`.
- `redirectToHttps` and HSTS keep browsers on HTTPS; configure forwarded headers behind a proxy.
- Hash passwords; encrypt only the columns that must be read back; rely on storage encryption for the rest.

## Example

Create the certificate and properties from the [SSL bundle card](#13_Spring_Boot/11_Securing_Data_in_Transit_and_at_Rest/concepts/https-with-an-ssl-bundle). Run any web example from earlier topics and call it over HTTPS, trusting the self-signed certificate explicitly.

```sh
./mvnw spring-boot:run
curl --cacert certs/server.crt https://localhost:8443/
```
