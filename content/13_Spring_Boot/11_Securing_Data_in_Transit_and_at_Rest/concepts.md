# Securing Data in Transit and at Rest

## HTTPS with an SSL bundle

TLS encrypts traffic between the client and the server and lets the client verify the server's identity from its certificate. An SSL bundle is Boot's named, reusable unit of TLS material: a key store with the certificate and private key, an optional trust store, and protocol options. Define the bundle once under `spring.ssl.bundle`, then refer to it by name from the web server or a client.

Generate a self-signed certificate for local testing with the command below and keep both files out of source control. `server.ssl.bundle` makes the embedded server use the bundle, and the server then serves only HTTPS on its port. Production certificates come from a certificate authority, often through the platform's certificate manager.

```sh
mkdir -p certs
openssl req -x509 -newkey rsa:2048 -nodes -days 30 -subj '/CN=localhost' \
  -addext 'subjectAltName=DNS:localhost' -keyout certs/server.key -out certs/server.crt
```

```properties
server.port=8443
server.ssl.bundle=web
spring.ssl.bundle.pem.web.keystore.certificate=file:certs/server.crt
spring.ssl.bundle.pem.web.keystore.private-key=file:certs/server.key
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/features/ssl.html)

## Reload rotated certificates

Certificates expire, and short-lived ones are rotated often. With `reload-on-update` set on a bundle, Boot watches the bundle's files and applies a new certificate and key without a restart. Changes are picked up after a quiet period, ten seconds by default, so a renewal tool can finish writing both files first.

The embedded Tomcat server supports hot reload when it uses a bundle. Replace both files in one step, for example by writing to temporary files and renaming them, so the server never reads a certificate with the wrong key. Monitor certificate expiry as well.

```properties
server.ssl.bundle=web
spring.ssl.bundle.pem.web.reload-on-update=true
spring.ssl.bundle.pem.web.keystore.certificate=file:certs/server.crt
spring.ssl.bundle.pem.web.keystore.private-key=file:certs/server.key
spring.ssl.bundle.watch.file.quiet-period=10s
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/features/ssl.html#features.ssl.reloading)

## Trust a private certificate authority

Clients need TLS configuration as well. Internal services often use certificates from a private certificate authority that the JVM does not trust by default. Define a bundle with only a trust store and apply it to a `RestClient` through `RestClientSsl`. Use mutual TLS by adding a key store to the same bundle.

The trust is scoped to this client, unlike a change to the JVM-wide trust store. Do not turn off certificate or hostname verification to make a connection work. Point the bundle at the correct certificate authority instead.

```properties
spring.ssl.bundle.pem.partner.truststore.certificate=file:certs/partner-ca.crt
```

```java
import org.springframework.boot.restclient.autoconfigure.RestClientSsl;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
class PartnerCatalog {
    private final RestClient client;

    PartnerCatalog(RestClient.Builder builder, RestClientSsl ssl) {
        this.client = builder.baseUrl("https://partner.example.internal")
                .apply(ssl.fromBundle("partner"))
                .build();
    }

    String titles() {
        return client.get().uri("/titles").retrieve().body(String.class);
    }
}
```

[Spring Boot docs](https://docs.spring.io/spring-boot/reference/io/rest-client.html#io.rest-client.restclient.ssl)

## Require HTTPS in the browser

When a load balancer or the app itself also accepts plain HTTP, send browsers to HTTPS before they submit anything. `redirectToHttps` in Spring Security redirects insecure requests to the HTTPS equivalent. For secure requests, Spring Security also writes the `Strict-Transport-Security` header by default. That HSTS header tells the browser to use only HTTPS for the host in later requests.

Behind a proxy that terminates TLS, the app sees plain HTTP. Set `server.forward-headers-strategy=native` (or `framework`) so the `X-Forwarded-Proto` header from a trusted proxy marks the request as secure. Otherwise the redirect loops and the HSTS header is never sent.

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
class HttpsConfig {
    @Bean
    SecurityFilterChain web(HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
                .formLogin(Customizer.withDefaults())
                .redirectToHttps(Customizer.withDefaults())
                .headers(headers -> headers.httpStrictTransportSecurity(hsts -> hsts.maxAgeInSeconds(31_536_000)));
        return http.build();
    }
}
```

[Spring Security docs](https://docs.spring.io/spring-security/reference/servlet/exploits/http.html)

## Encrypt sensitive columns

Data at rest is protected in layers. Use the database's or disk's encryption against stolen storage, and hash passwords so they cannot be read back, as in the [password encoding card](#13_Spring_Boot/08_Spring_Security_Foundations/concepts/users-and-password-encoding). Encrypt individual columns that the app must read back but that a database user, backup, or log should not see in plain text, such as a member's phone number.

A JPA `AttributeConverter` encrypts on write and decrypts on read. `Encryptors.delux` from Spring Security Crypto uses 256-bit AES-GCM with a key derived from a password and salt. Boot lets Hibernate obtain converters from Spring, so this converter can receive its secrets through its constructor. Load the secrets from the environment or a secrets manager. Encrypted columns cannot be searched with ordinary `WHERE` clauses.

```java
import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Convert;
import jakarta.persistence.Converter;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.encrypt.Encryptors;
import org.springframework.security.crypto.encrypt.TextEncryptor;
import org.springframework.stereotype.Component;

@Component
@Converter
class EncryptedText implements AttributeConverter<String, String> {
    private final TextEncryptor encryptor;

    EncryptedText(@Value("${study.crypto.password}") String password, @Value("${study.crypto.salt}") String hexSalt) {
        this.encryptor = Encryptors.delux(password, hexSalt);
    }

    @Override
    public String convertToDatabaseColumn(String plain) {
        return plain == null ? null : encryptor.encrypt(plain);
    }

    @Override
    public String convertToEntityAttribute(String stored) {
        return stored == null ? null : encryptor.decrypt(stored);
    }
}

@Entity
class Member {
    @Id @GeneratedValue Long id;
    String name;

    @Convert(converter = EncryptedText.class)
    String phone;
}
```

[Spring Security docs](https://docs.spring.io/spring-security/reference/features/integrations/cryptography.html)
