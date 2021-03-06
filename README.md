# Vault Testing

This is a testing respository solely used to get used to working with Vault. Its a set of instructions for getting my vault up and running. The keys and tokens present in this repo are there in order to support a working demo, and should not be reused elsewhere.

## Setup 

Download the command line tool (linux): 

```
wget https://releases.hashicorp.com/vault/0.10.1/vault_0.10.1_linux_amd64.zip
unzip vault_0.10.1_linux_amd64.zip
```

Start the container:

```
docker-compose up 
```

The next command is for first time setup. Delete the contents of `data/` and start here if you want to do setup again from scratch.

```bash
# Initialize the vault for first use. Save the output for later.
# THe unseal keys are required every time the vault is started.
# The token is required to interact with the vault via the command line tool.
$ ./vault init
Unseal Key 1: sXcvFFXaL9gi+4MkS3Ov6Kyj4Cu/DaFiFKBlZf/X1dpW
Unseal Key 2: NvQGZTO1TkB0q54OuuzPfDLchs0HDhD//8DGVJTC4TEJ
Unseal Key 3: LWT0neh4PRzRaEK0E2961x+8LHnihb43Tawga2wHykWZ
Unseal Key 4: RNvZESD2AnjvLhggwTZJsocRhOH49fe4Zq5n4NI7QliO
Unseal Key 5: f5VRCd5yXRUK/IflMZ2heS0IQ05mohKtrPx82LyRJPm6

Initial Root Token: 73525826-cda0-b580-f93b-cec000e22c24
...
```

Export the token from the output above and the URL of the running instance for the command line tool:

```
export VAULT_TOKEN=30419a3a-8c1c-6faf-3849-88841250864f
export VAULT_ADDR='http://127.0.0.1:8200'
```

To play around with the python client:

```
pipenv install
pipenv shell
python tester.py
```

## Tasks

### PKI

### Setting up PKI

```
vault secrets enable pki
```

PKI Quickstart with external root CA using intermediate endpoint (prefer this):

```bash
# Generate root keypair
openssl genrsa -out keys/lhr.key 4096

# Generate self-signed root cert
openssl req -new -config ca.conf -x509 -key keys/lhr.key -out keys/lhr.crt

# Generate intermediate CSR. Copy the resulting CSR into a file keys/vault.csr
./vault write pki/intermediate/generate/internal \
    common_name=vault.lhr \
    ttl=87600h \
    key_bits=4096

# Sign the intermediate vault cert using the self-signed root. Ca.ext required in order to validate the extensions
openssl x509 -req -in keys/vault.csr -CA keys/lhr.crt -CAkey keys/lhr.key -CAcreateserial -out keys/vault.crt -extfile ca.ext 

# Pass the newly signed cert into vault
./vault write pki/intermediate/set-signed certificate="$(cat keys/vault.crt)"
```

This version generates the keys outside of the vault. Prefer the first method because the keys never leave the vault.

#### Interacting with PKI

The vault command line tool uses `/pki/cert/ca`, but normal HTTP endpoints should hit `/pki/ca`. Read the CA's cert at the command line:

```
./vault read /pki/cert/ca
```


Create a CSR outside of vault and pass it to vault for signing:

```bash
# Create new key (the one-line form might work here, too)
openssl genrsa -out keys/brian.key 4096

# Create CSR with pre-filled subject
openssl req -new -key keys/brian.key -out keys/brian.csr -subj "/C=GB/ST=London/L=London/O=Global Security/OU=IT Department/CN=brian.developer.lhr"

./vault write pki/sign/developer \
    common_name=brian.developer.lhr \
    csr="$(cat keys/brian.csr)"
```


### Policies and Roles

See [policy documentation](https://www.vaultproject.io/docs/concepts/policies.html#creating-policies)

Read current roles: 

```
vault read sys/policy
```


Create a new role and issue a new cert under it:

```bash
# Create a new role
./vault write pki/roles/developer \
    allowed_domains=developer.lhr \
    allow_subdomains=true \
    max_ttl=8760h \
    key_bits=4096

# Create the new entity and download key, cert, and issuing CA
./vault write pki/issue/developer common_name=mickey.developer.lhr 
```

Note to self: this one might be useful for provisioning, but since keys are returned and exist on the device, its a little less secure.


### Authentication

[Auth docs](https://www.vaultproject.io/docs/auth/cert.html).

Enable certificate auth:

```bash
vault auth enable cert
```

Set a trusted cert to auth against. Here I'm just using the vault's cert, but I'm not sure it will work. NOTE: this has to be on TLS.

```bash
# Create a default login profile. This may not have any roles attached to it
./vault write auth/cert/certs/default \
    certificate="$(cat keys/vault.crt)" \
    ttl=3600

# Try to login 
./vault login \
    -method=cert \
    -client-cert=keys/brian.crt \
    -client-key=keys/brian.key 
```

Ok, I'm not sure I understand this. So I can't sign certs with a single CA and then distribute them with ACLs derived in some other way? It seems the cert system requires that each possible role have its own certificate, right?

Does that mean I have to make a sub CA for each one and host it at a different PKI endpoint? Seems clunky, but maybe I'm missing something. 

There's also another possibility: skip auth, distribute SSH for now, and come back later for the rest of Vault.

Actually, [token authentication](https://www.vaultproject.io/api/auth/token/index.html) doesn't seem like a bad idea. Instead of CSRs and keys, 

## Misc Useful Commands

Examine a CSR: 

```
openssl req -in keys/vault.csr -noout -text
```

Examine a Cert:

```
openssl x509 -in keys/vault.crt -text -noout
```

Examine a cert hosted on vault without downloading it:

```
curl -s http://localhost:8200/v1/cuddletech_ops/ca/pem | openssl x509 -text | head -20
```

Extract public key:

```bash
openssl rsa -in keys/root.lhr -pubout -out keys/root.lhr.pubkey
```

Validate a cert against its signer (only works against the root, not intermediates):

```
openssl verify -CAfile keys/lhr.crt keys/vault.crt 
```

## Roles

A role is a name assignment paired with an ACL. Here are the possible activities controlled by the vault:

- Authenticate with the vault
- Create new developer 
- Create a copy of a developer's keys and certs
- Create new device 
- Grant SSH access to a device
- Grant AWS access
- Sign a build
- Connect to MQTT
- Upload build to ECR


## Resources

This might be a useful [link](https://www.melvinvivas.com/secrets-management-using-docker-hashicorp-vault/) for setting up the container with config and intended caps.

See also [here](https://medium.com/@pcarion/a-consul-a-vault-and-a-docker-walk-into-a-bar-d5a5bf897a87) for getting configuration into the container, though it might be easier to just map in an external file. I just don't know how to do that yet. 

The official [pki docs](https://www.vaultproject.io/docs/secrets/pki/index.html).

[The most common OpenSSL commands](https://www.sslshopper.com/article-most-common-openssl-commands.html).

[A great gist](https://gist.github.com/Soarez/9688998) for setting up self-signed PKIs.

[Vault PKI tutorial](https://blog.kintoandar.com/2015/11/vault-PKI-made-easy.html).

On getting python websockets to use [self-signed certs](https://websockets.readthedocs.io/en/stable/intro.html#secure-example) as a client or a server.

## TODO

- Revocation
- Refresh (ideally with the same keys)
- Distribution to Developers
- Authenticating TO vault with certs
- Role definitions

## Scratch

For my local mac machine: 

```
Unseal Key 1: dhG5/C1ldpJeM85VDx63Go3Azq56rlsFwX9I0RXS9YdQ
Unseal Key 2: hVm2OzERaHsiRTIgI52oN+YPbTtUTXEYp66yLgJgK59+
Unseal Key 3: 6r3rIpL4ssRaGLUs/JVF6UYmco1NWSDgJYWu86Eiz93F
Unseal Key 4: Rj7ptRDBMeZrHMe7SIj78Tm8NT3FKmpmBu5sZK2jz0zq
Unseal Key 5: HkXcBbOAXdWTrB7eBFVWXBTLg4WX99NE8nX+eW4kgPda

Initial Root Token: 30419a3a-8c1c-6faf-3849-88841250864f
```

