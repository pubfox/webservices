import unittest

from jnius import autoclass as Java
EncryptHandler = Java('cc.yun.util.Encrypt')

class TestJavaHandler(unittest.TestCase):

    def test_get_encrypt(self):
        password = 'qweeee'
        xml = '<a>b</a>'
        encrypt = EncryptHandler.get_encrypt_by_password(xml, password)
        encrypt_known = 'CC7BCB7F69B7784BAF6A0B66B11263D7'
        self.assertEquals(encrypt, encrypt_known)
        
        encrypt_decrypt = EncryptHandler.get_decrypt_by_password(encrypt, password)
        self.assertEquals(xml, encrypt_decrypt)

if __name__ == '__main__':
    unittest.main()