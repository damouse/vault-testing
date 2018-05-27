import os

import hvac

TOKEN = '289c442f-3bf1-3608-af0c-86dc6ffe1719'


def main():
    # Using plaintext
    # client = hvac.Client()
    # client = hvac.Client(url='http://localhost:8200')
    client = hvac.Client(url='http://localhost:8200', token=TOKEN)

    print("Authenticated")

    client.write('/secret/foo', baz='bar', lease='1h')
    print(client.read('/secret/foo'))
    client.delete('/secret/foo')


if __name__ == '__main__':
    main()
