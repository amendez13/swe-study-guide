# Security Hardening

Most web attacks exploit a few patterns: unencoded output, forged requests, loose CORS, unchecked redirects, string-built SQL, and missing ownership checks.

## Key points

- Let Razor encode output, encode for the right context elsewhere, and add a Content Security Policy.
- Use antiforgery tokens with cookie authentication, and list exact origins in CORS policies.
- Redirect only to local URLs, parameterize SQL, check ownership on every id, and store passwords as hashes with Identity.

## Example

Run the [CORS example](#12_ASP.NET_Core/29_Security_Hardening/concepts/cross-origin-requests-and-cors) and compare an allowed and a foreign origin.

```sh
curl -i -H 'Origin: https://app.example.org' http://127.0.0.1:5080/api/books
curl -i -H 'Origin: https://evil.example' http://127.0.0.1:5080/api/books
```

The response is 200 both times. Only the first carries `Access-Control-Allow-Origin`, so a browser would hide the second response from the calling script. The [SQL injection example](#12_ASP.NET_Core/29_Security_Hardening/concepts/sql-injection) needs the EF Core SQLite package from [chapter 12](#12_ASP.NET_Core/12_Entity_Framework_Core).
