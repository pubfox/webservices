#coding=utf8
import unittest

from jnius import autoclass as Java
EncryptHandler = Java('cc.yun.util.EncryptTest')
password = 'qweeee'

class TestJavaHandler(unittest.TestCase):

    def test_get_encrypt(self):
        xml = '<a>b</a>'
        encrypt = EncryptHandler.get_encrypt_by_password(xml, password)
        encrypt_known = 'CC7BCB7F69B7784BAF6A0B66B11263D7'
        self.assertEquals(encrypt, encrypt_known)

    def test_get_decrypt(self):
        encrypt = 'F4EA5AA5DDB4B96BE4038919D78A2E07'
        decrypt = EncryptHandler.get_decrypt_by_password(encrypt, password)
        decrypt_known = '<a>中文</a>'
        self.assertEquals(decrypt, decrypt_known)


if __name__ == '__main__':
    unittest.main()
