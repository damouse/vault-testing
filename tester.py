import os

import hvac

TOKEN = '73525826-cda0-b580-f93b-cec000e22c24'


def main():
    client = hvac.Client(url='http://localhost:8200', token=TOKEN)
    print("Authenticated")

    # client.write('/secret/foo', baz='bar', lease='1h')
    print(client.read('/secret/hello'))
    # client.delete('/secret/foo')


if __name__ == '__main__':
    main()
