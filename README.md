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
export VAULT_TOKEN=216c2622-43f9-731e-f673-624f0d0145d3
export VAULT_ADDR='http://127.0.0.1:8200'
```

To play around with the python client:

```
pipenv install
pipenv shell
python tester.py
```

## Tasks

Set and read secrets:

```
./vault kv put secret/hello foo=world
./vault kv get secret/hello
```

Turn on PKI:

```
vault secrets enable pki
```


PKI Quickstart with self-signed root:

```bash
# Change the root lease to 10 years
./vault secrets tune -max-lease-ttl=87600h pki

# Generate the root cert
./vault write pki/root/generate/internal common_name=myvault.com ttl=87600h

# Set CRL and issuing URLs
./vault write pki/config/urls issuing_certificates="http://127.0.0.1:8200/v1/pki/ca" crl_distribution_points="http://127.0.0.1:8200/v1/pki/crl"

# Configure a role (maps to a policy)
./vault write pki/roles/example-dot-com \
    allowed_domains=example.com \
    allow_subdomains=true max_ttl=72h

# Issue a new cert under the newly created role 
./vault write pki/issue/example-dot-com \
    common_name=blah.example.com
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
openssl x509 -req -in keys/vault.internal.csr -CA keys/lhr.crt -CAkey keys/lhr.key -CAcreateserial -out keys/vault.crt -extfile ca.ext 

# Pass the newly signed cert into vault
./vault write pki/intermediate/set-signed certificate="$(cat keys/vault.crt)"
```

Since I'm having trouble siging the intermediate, this generates the root cert and keys in one step, ensuring CA:true is set under extensions. This method doesn't go through the intermediate generation from vault. It also doesn't correctly send the cert back up to vault.

```bash
# Generate a key for the CA
openssl genrsa -out keys/vault.key 4096

# CSR
openssl req -config ca.conf -new -key keys/vault.key -out keys/vault.csr

# Sign the cert, ensuring that CA:TRUE is set
openssl x509 -req -in keys/vault.csr -CA keys/root.lhr.crt -CAkey keys/root.lhr.pem -CAcreateserial -out keys/vault.crt -days 3650

# Upload the cert and key to vault. NOTE: the resulting file is not the right format. Also the included keys are not what vault is expecting
./vault write pki/config/ca \
    pem_bundle="$(cat keys/vault.key)\n$(cat keys/vault.crt)"
```

Attempt #3, Root CA:

```bash
# Keys, vault and root
openssl genrsa -out keys/lhr.key 4096
openssl genrsa -out keys/vault.key 4096

# Generate root cert
openssl req -x509 -new -config ca.conf -key keys/lhr.key -out keys/lhr.crt 

# Generate a CSR
openssl req -config ca.conf -new -key keys/vault.key -out keys/vault.csr

# Sign the CSR (WORKS!)
openssl x509 -req -in keys/vault.csr -CA keys/lhr.crt -CAkey keys/lhr.key -CAcreateserial -out keys/vault.crt -days 3650 -extfile ca.ext 

# Upload the cert and keys to vault (note: this command doesnt work-- just copy and paste the cert and key into a string)
./vault write pki/config/ca \
    pem_bundle="$(cat keys/vault.crt)\n$(cat keys/vault.key)"
```

Trying with internal vault CSR:

```

```

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

## Resources

This might be a useful [link](https://www.melvinvivas.com/secrets-management-using-docker-hashicorp-vault/) for setting up the container with config and intended caps.

See also [here](https://medium.com/@pcarion/a-consul-a-vault-and-a-docker-walk-into-a-bar-d5a5bf897a87) for getting configuration into the container, though it might be easier to just map in an external file. I just don't know how to do that yet. 

The official [pki docs](https://www.vaultproject.io/docs/secrets/pki/index.html).

[The most common OpenSSL commands](https://www.sslshopper.com/article-most-common-openssl-commands.html).

[A great gist](https://gist.github.com/Soarez/9688998) for setting up self-signed PKIs.

[Vault PKI tutorial](https://blog.kintoandar.com/2015/11/vault-PKI-made-easy.html).

## TODO

- Cert validation in python 
- Revocation
- Refresh (ideally with the same keys)
- Plan API for developer and other intermediate issuance


## Scratch

For my local mac machine: 

```
Unseal Key 1: kcdm7d3po4J1eYiKzeR8O8LslwgLEREnDfKHN0rT3md/
Unseal Key 2: HJIAOb9GE3nM9YIsSP7xg4psgMED4JYd2gglwvFGBfuC
Unseal Key 3: 5anDtCWj7LHTItv1WFH6d/mCqrSek4ns8OxD3N/lluJN
Unseal Key 4: AC25iLawrw6Tjtok8E/udGwcACcuIEm54YhJpjv5FDAb
Unseal Key 5: qCLbIjdiIhw76AczMq8EaHBvwvGjFGrWwaujRGnDnmqS

Initial Root Token: 216c2622-43f9-731e-f673-624f0d0145d3
```

