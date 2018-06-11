
import hvac
from OpenSSL import crypto


TOKEN = '73525826-cda0-b580-f93b-cec000e22c24'


def connect_test():
    client = hvac.Client(url='http://localhost:8200', token=TOKEN)
    print("Authenticated")

    # client.write('/secret/foo', baz='bar', lease='1h')
    print(client.read('/secret/hello'))
    # client.delete('/secret/foo')


def examine_certs():
    cert_file = 'keys/lhr.crt'
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cert_file).read())
    pubKeyObject = cert.get_pubkey()

    # Use .CN to get the common name
    print('Subject: ', cert.get_subject())
    print('Issued by: ', cert.get_issuer())
    print('Public key: ', crypto.dump_publickey(crypto.FILETYPE_PEM, pubKeyObject))

    # Validation: https://gist.github.com/uilianries/0459f59287bd63e49b1b8ef03b30d421
    # See here for full trust chain checking: http://aviadas.com/blog/2015/06/18/verifying-x509-certificate-chain-of-trust-in-python/


def verify_certificate_chain(cert_path, trusted_certs):
    """ Validation requires the FULL chain be passed in as trusted_certs-- meaning vault's current 
    cert and the root cert.
    """
    # Download the certificate from the url and load the certificate
    cert_file = open(cert_path, 'r')
    cert_data = cert_file.read()
    certificate = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)

    # Create a certificate store and add your trusted certs
    try:
        store = crypto.X509Store()

        # Assuming the certificates are in PEM format in a trusted_certs list
        for _cert in trusted_certs:
            cert_file = open(_cert, 'r')
            cert_data = cert_file.read()
            client_certificate = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
            store.add_cert(client_certificate)

        # Create a certificate context using the store and the downloaded certificate
        store_ctx = crypto.X509StoreContext(store, certificate)

        # Verify the certificate, returns None if it can validate the certificate
        store_ctx.verify_certificate()

        print('Cert check for: ', cert_path, ' against ', trusted_certs, ' OK')
        return True

    except Exception as e:
        print(e)
        return False


def examine_revocation():
    # CRLs: https://stackoverflow.com/questions/4115523/is-there-a-simple-way-to-parse-crl-in-python
    # Used wget on the CRL endpoint, but its not the right format
    file = 'scratch/crl.pem'
    crl = crypto.load_crl(crypto.FILETYPE_PEM, open(file, 'rb').read())

    for rvk in crl.get_revoked():
        print("Serial:", rvk.get_serial())


def cert_testing():
    verify_certificate_chain('keys/mick.crt', ['keys/vault.crt', 'keys/lhr.crt'])


if __name__ == '__main__':
    cert_testing()
    # examine_certs()
    # examine_revocation()
