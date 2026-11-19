# Minimal API Binding and Validation

Binding sources determine where inputs come from. Validation runs on successfully bound inputs and applies rules you declare to the model.

## Key points

- Make ambiguous binding sources explicit. Use nullable or defaulted arguments for intentional omissions.
- Form uploads require their matching antiforgery cookie and token with the .NET 10 defaults in the [upload example](#12_ASP.NET_Core/07_Minimal_API_Binding_and_Validation/concepts/multipart-uploads-and-antiforgery).
- Register built-in Minimal API validation to enforce annotations before the handler runs.

## Example

Run the [automatic validation example](#12_ASP.NET_Core/07_Minimal_API_Binding_and_Validation/concepts/automatic-minimal-api-validation) and change the seat count from zero to one. Compare the status and response body.

```sh
curl -i http://127.0.0.1:5080/reservations \
  -H 'Content-Type: application/json' \
  -d '{"room":"maps","seats":0}'
```

For the [multipart example](#12_ASP.NET_Core/07_Minimal_API_Binding_and_Validation/concepts/multipart-uploads-and-antiforgery), run the following from a scratch directory while that example is serving.

```sh
printf 'reading notes\n' > reading.txt
token=$(curl -fsS -c cookies.txt http://127.0.0.1:5080/upload-token)
curl -i -b cookies.txt -H "RequestVerificationToken: $token" \
  -F 'file=@reading.txt' http://127.0.0.1:5080/uploads
```
