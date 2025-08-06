from base64 import b64decode

from hssp.utils.crypto import decrypt_aes_256_cbc_pad7, evp_bytes_to_key


def aes_decrypt(data: str, password: str):
    raw = b64decode(data)
    salt = raw[8:16]
    key, iv = evp_bytes_to_key(password, salt, 32, 16, "md5")
    text = decrypt_aes_256_cbc_pad7(raw[16:], key, iv)
    return text.decode()


def main():
    result = aes_decrypt(
        "U2FsdGVkX1992Te93N/z9WCCxQXWZOM4pyA3PXmj1RwBWLb9MiRA9t4tEKPWhCVA", "952605d2c779d8f04fb7ffe276bbf834"
    )
    print(result)


if __name__ == "__main__":
    main()
