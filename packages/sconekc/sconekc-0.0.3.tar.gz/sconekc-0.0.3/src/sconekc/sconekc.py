'''
###
# Andre Miguel @ Scontain -- amiguel @ scontain . com
# Set of functions to handle Keycloak access and validation tokens; and JSON and JWT payload
# some work is based on the works from [ixe013] https://gist.github.com/ixe013/f3a7ca48e327a7652554f29be3ee7d46
'''

import os
import socket
import ssl
import hashlib
import json, requests
from datetime import datetime

import base64
import os.path
import pprint
import sys
import time
import zlib

import cryptography.x509
import cryptography.hazmat.backends
import cryptography.hazmat.primitives
DEFAULT_FINGERPRINT_HASH = cryptography.hazmat.primitives.hashes.SHA256


# [ixe013]
def pad_base64(data):
    """Makes sure base64 data is padded
    """
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += '='* (4 - missing_padding)
    return data


# [ixe013]
def decompress_partial(data):
    """Decompress arbitrary deflated data. Works even if header and footer is missing
    """
    decompressor = zlib.decompressobj()
    return decompressor.decompress(data)


# [ixe013]
def decompress(JWT):
    """Split a JWT to its constituent parts. 
    Decodes base64, decompress if required. Returns but does not validate the signature.
    """
    header, jwt, signature = JWT.split('.')

    printable_header = base64.urlsafe_b64decode(pad_base64(header)).decode('utf-8')

    if json.loads(printable_header).get("zip", "").upper() == "DEF":
        printable_jwt = decompress_partial(base64.urlsafe_b64decode(pad_base64(jwt)))
    else:
        printable_jwt = base64.urlsafe_b64decode(pad_base64(jwt)).decode('utf-8')

    # printable_signature = base64.urlsafe_b64decode(pad_base64(signature))

    return json.loads(printable_header), json.loads(printable_jwt), signature


# [ixe013]
def showJWT(JWT):
    header, jwt, signature = decompress(JWT)

    print("Header:  ", end="")
    pprint.pprint(header)

    print("Token:   ", end="")
    pprint.pprint(jwt)

    print("Signature:   ", end="")
    pprint.pprint(signature)

    print("Issued at:  {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt['iat'])) if 'iat' in jwt else 'Undefined'))
    print("Not before: {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt['nbf'])) if 'nbf' in jwt else 'Undefined'))
    print("Expiration: {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt['exp'])) if 'exp' in jwt else 'Undefined'))


# mig based on [ixe013]
def sliceJWT(JWT):
    header, jwt, signature = decompress(JWT)

    issued="Issued at:  {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt['iat'])) if 'iat' in jwt else 'Undefined')
    started="Not before: {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt['nbf'])) if 'nbf' in jwt else 'Undefined')
    validto="Expiration: {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jwt['exp'])) if 'exp' in jwt else 'Undefined')

    return (header, jwt, signature, issued, started, validto)


# mig
def get_access_token(server, realm, client, username, password, cert='cert.pem', key='key.pem'):
    aturl="protocol/openid-connect/token"

    sessionkeycloak = requests.Session()
    sessionkeycloak.cert=(cert, key)

    try:
        url=f"{server}/realms/{realm}/{aturl}"
        response = sessionkeycloak.post(url,
            headers={"Content-Type":"application/x-www-form-urlencoded"},
            data={"client_id":client, "username":username, "password":password, "grant_type":"password"}, verify=False)
        if(response.status_code != 200):
            return "[ERR]HTTP STATUS CODE:",response.status_code,". Body:",response.json()
        access_token = response.json()['access_token']
        if(access_token == None or access_token == ''):
            return "[ERR]Invalid access token. Body:", response.json()
        return access_token
    except (requests.exceptions.ConnectionError, OSError) as errcnx:
        print("[ERR]Exception:", errcnx.strerror)
        print("[ERR]Exception:", errcnx)
        return f"[ERR]Exception: {errcnx.strerror}, {errcnx}"


# mig
def get_validation_token_simple(server, realm, access_token, cert='cert.pem', key='key.pem'):
    vturl="protocol/openid-connect/userinfo"

    sessionkeycloak = requests.Session()
    sessionkeycloak.cert=(cert, key)

    try:
        url=f"{server}/realms/{realm}/{vturl}"
        response = sessionkeycloak.post(url,
            headers={"Authorization":"Bearer "+access_token},
            verify=False)
        if(response.status_code != 200):
            return "[ERR]HTTP STATUS CODE:",response.status_code,". Body:",response.json()
        s_validation_token = str(response.json()).replace("'", '"').replace(r"True","true").replace(r"False","false")
        b_validation_token = bytes(str(s_validation_token).encode('utf-8'))
        j_validation_token = json.loads(str(b_validation_token.decode('utf-8')))
        return j_validation_token
    except (requests.exceptions.ConnectionError, OSError) as errcnx:
        print("[ERR]Exception:", errcnx.strerror)
        print("[ERR]Exception:", errcnx)
        return f"[ERR]Exception: {errcnx.strerror}, {errcnx}"


# mig
def get_validation_token(server, realm, access_token, cert='cert.pem', key='key.pem'):
    vturl="protocol/openid-connect/userinfo"

    sessionkeycloak = requests.Session()
    sessionkeycloak.cert=(cert, key)

    try:
        url=f"{server}/realms/{realm}/{vturl}"
        response = sessionkeycloak.post(url,
            headers={"Authorization":"Bearer "+access_token},
            verify=False)
        if(response.status_code != 200):
            return "[ERR]HTTP STATUS CODE:",response.status_code,". Body:",response.json()
        s_validation_token = str(response.json()).replace("'", '"').replace(r"True","true").replace(r"False","false")
        b_validation_token = bytes(str(s_validation_token).encode('utf-8'))
        j_validation_token = json.loads(str(b_validation_token.decode('utf-8')))
        # enriching with clearer information from access token
        #j_access_token = json.loads(base64.urlsafe_b64decode(access_token + '=' * (4 - len(access_token) % 4)).decode('utf-8'))
        header, jwt, signature, issued, started, validto = sliceJWT(access_token)
        j_validation_token["accesstokentimestampissuing"] = jwt["iat"]
        j_validation_token["accesstokendatetimeissuing"] = issued
        j_validation_token["accesstokentimestampexpiring"] = jwt["exp"]
        j_validation_token["accesstokendatetimeexpiring"] = validto
        j_validation_token["validationtokentimestampvalidation"] = int(datetime.timestamp(datetime.now()))
        j_validation_token["validationtokendatetimevalidation"] = "Validated on: {} (localtime)".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(j_validation_token["validationtokentimestampvalidation"])))
        return j_validation_token
    except (requests.exceptions.ConnectionError, OSError) as errcnx:
        print("[ERR]Exception:", errcnx.strerror)
        print("[ERR]Exception:", errcnx)
        return f"[ERR]Exception: {errcnx.strerror}, {errcnx}"
