# Vault Testing

This is a testing respository solely used to get used to working with Vault. Its a set of instructions for getting my vault up and running.

Download the command line tool with: 

```
wget https://releases.hashicorp.com/vault/0.10.1/vault_0.10.1_linux_amd64.zip
unzip vault_0.10.1_linux_amd64.zip
```

Run the container with `docker-compose up`.

```
export VAULT_TOKEN=73525826-cda0-b580-f93b-cec000e22c24
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

PKI Quickstart

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

## Resources

This might be a useful [link](https://www.melvinvivas.com/secrets-management-using-docker-hashicorp-vault/) for setting up the container with config and intended caps.

See also [here](https://medium.com/@pcarion/a-consul-a-vault-and-a-docker-walk-into-a-bar-d5a5bf897a87) for getting configuration into the container, though it might be easier to just map in an external file. I just don't know how to do that yet. 

The official [pki docs](https://www.vaultproject.io/docs/secrets/pki/index.html).

## TODO

- Cert validation in python 
- Revocation
- Refresh (ideally with the same keys)
- Plan API for developer and other intermediate issuance

## Scratch

```
Unseal Key 1: 9cJnvuLCiUblxNutVNEmOrXAAvqo7Usy3sKm2lxxVDQs
Unseal Key 2: 3XDGfGR9XXXe0k198ni8FtRC+kVLwmveJ9LHfDD1XUb3
Unseal Key 3: NHpHQliLU/tgRmPbx9dORpnisuRjouePbS/oJFgDQo0I
Unseal Key 4: qIOx4Uk7zWsfNMdNIqByi++cNBplxbJ3iJ2D6289S6uW
Unseal Key 5: 9pLKkIGI7mMAaspnAIPYOVwzGslHQqfDckcgczOq8+RK

Initial Root Token: 73525826-cda0-b580-f93b-cec000e22c24
```
