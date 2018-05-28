
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

    cert_file = 'scratch/root.pem'
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cert_file).read())
    pubKeyObject = cert.get_pubkey()

    # Use .CN to get the common name
    print('Subject: ', cert.get_subject())
    print('Issued by: ', cert.get_issuer())
    print('Public key: ', crypto.dump_publickey(crypto.FILETYPE_PEM, pubKeyObject))

    # Validation: https://gist.github.com/uilianries/0459f59287bd63e49b1b8ef03b30d421


def examine_revocation():
    # CRLs: https://stackoverflow.com/questions/4115523/is-there-a-simple-way-to-parse-crl-in-python
    # Used wget on the CRL endpoint, but its not the right format
    file = 'scratch/crl.pem'
    crl = crypto.load_crl(crypto.FILETYPE_PEM, open(file, 'rb').read())

    for rvk in crl.get_revoked():
        print("Serial:", rvk.get_serial())


if __name__ == '__main__':
    # examine_certs()
    examine_revocation()
