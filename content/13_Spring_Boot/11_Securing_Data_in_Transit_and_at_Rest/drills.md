# Securing Data in Transit and at Rest — Drills

Predict the result before running the example.

## Predict the client failure

The partner service uses a certificate signed by the company's private CA. The client below calls it with the default `RestClient.Builder`. What happens, and what is the safe fix?

```java
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
class PartnerStatus {
    private final RestClient client;

    PartnerStatus(RestClient.Builder builder) {
        this.client = builder.baseUrl("https://partner.example.internal").build();
    }

    String status() {
        return client.get().uri("/status").retrieve().body(String.class);
    }
}
```

**Answer**

The TLS handshake fails with a certificate path error, because the JVM's default trust store does not contain the private CA. Define a bundle whose trust store is the CA certificate and apply it with `RestClientSsl.fromBundle`, as in [trust a private certificate authority](#13_Spring_Boot/11_Securing_Data_in_Transit_and_at_Rest/concepts/trust-a-private-certificate-authority). Never install a trust-all manager.

## Choose hashing or encryption

For each field, choose a password hash, column encryption, or neither: a member's login password, a member's phone number that staff call, and a book's title. Explain the phone number choice.

```java
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;

@Entity
class MemberRecord {
    @Id @GeneratedValue Long id;
    String passwordHash;
    String phone;
    String favoriteBookTitle;
}
```

**Answer**

Hash the password with the delegating `PasswordEncoder`, because the app only needs to compare it. Encrypt the phone number with a converter such as [`EncryptedText`](#13_Spring_Boot/11_Securing_Data_in_Transit_and_at_Rest/concepts/encrypt-sensitive-columns), because staff must read it back while database dumps should not reveal it. The title is not sensitive; storage-level encryption covers it.
