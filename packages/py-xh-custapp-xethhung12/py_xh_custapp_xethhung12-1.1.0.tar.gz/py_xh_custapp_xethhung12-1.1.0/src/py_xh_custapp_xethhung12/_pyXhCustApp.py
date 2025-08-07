import os
import sys
from os.path import isfile, join
from pathlib import Path
from typing import Optional
import hashlib
from pathlib import Path
import base64
from Crypto import Random
from Crypto.Cipher import AES
import random

class _EncryptionTools:
    @staticmethod
    def hex_format(data: bytes)->str:
        return data.hex()

    @staticmethod
    def hex_decoding(data: str)->bytes:
        return bytes.fromhex(data)

    @staticmethod
    def b64_format(data: bytes)->str:
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def b64_decoding(data: str)->bytes:
        return base64.b64decode(data.encode('utf-8'))

    @staticmethod
    def encrypt_data(key, data: str)->(str, str, str): 
        n = Random.new().read(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=n)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        return _EncryptionTools.b64_format(ciphertext), _EncryptionTools.hex_format(n), _EncryptionTools.hex_format(tag)

    @staticmethod
    def decrypt_data(key: str, ciphertext:str, nonce:str, tag:str)->str|None:
        key = _EncryptionTools.b64_decoding(key)
        ciphertext = _EncryptionTools.b64_decoding(ciphertext)
        nonce = _EncryptionTools.hex_decoding(nonce)
        tag = _EncryptionTools.hex_decoding(tag)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        data = cipher.decrypt(ciphertext).decode('utf-8')
        try:
            cipher.verify(tag)
        except Exception as ex:
            print(ex)
            return None
        return data

class Platform:
    @staticmethod
    def is_win():
        return sys.platform == 'win32'

    @staticmethod
    def is_linux():
        return sys.platform == 'linux'

    @staticmethod
    def separator():
        if Platform.is_win():
            return '\\'
        elif Platform.is_linux():
            return '/'
        else:
            raise Exception("Unknown separator")


def _has_file(home, name: str) -> bool:
    return len([fileName for fileName in os.listdir(home) if fileName == name and isfile(join(home, fileName))]) == 1


def _get_file_content(path: str) -> Optional[str]:
    if os.path.exists(path):
        with open(path, "r") as file:
            return file.read().strip()
    else:
        return None


_PROXY_VAL = "proxy"


class CustApp:

    def _get_credential_file(self)->str:
        return os.path.abspath(join(self.home, "cc"))
    
    def _get_cc_hash_str(self)->str:
        return _EncryptionTools.b64_format(hashlib.sha256(self._get_credential_file().encode('utf-8')).digest())

    def _get_default_cred(self)->bytes:
        """
        Hashes an input string, uses the hash as a seed for the random number generator,
        and returns the first 32 random bits as an integer.
        """
        seed_value = self._get_cc_hash_str()
        random.seed(seed_value)
        random_bits = random.getrandbits(256).to_bytes(32, byteorder='big')
        return random_bits


    def __init__(self, home: Path, name: str):
        self.separator = Platform.separator()
        self.home = join(str(home), ".pyXhCustApp", name)
        if os.path.exists(self.home) and os.path.isfile(self.home):
            raise Exception("Home %s is not directory!" % self.home)
        elif not os.path.exists(self.home):
            os.makedirs(self.home)

        if not os.path.exists(self.home) or os.path.isfile(self.home):
            raise Exception("Home %s is not valid!" % self.home)
        
        if Platform.is_win():
            import ctypes
            FILE_ATTRIBUTE_HIDDEN = 0x02
            try:
                attrs = ctypes.windll.kernel32.GetFileAttributesW(str(self.home))
                if attrs == -1:
                    raise FileNotFoundError(f"Path not found: {path}")
                return bool(attrs & FILE_ATTRIBUTE_HIDDEN)
            except Exception as e:
                print(f"Error: {e}")
                return False

        if os.path.exists(self._get_credential_file()) and not os.path.isfile(self._get_credential_file()):
            raise Exception("Credential file path contains non file structure")

        if not os.path.exists(self._get_credential_file()):
            with open(self._get_credential_file(), "w") as f:
                f.write(self._get_cc_hash_str())
        elif Path(self._get_credential_file()).stat().st_size == 0:
            with open(self._get_credential_file(), "w") as f:
                f.write(self._get_cc_hash_str())
        
        if not os.path.exists(self._get_credential_file()):
            raise Exception("Missing the credential file")
        

    def has_proxy(self) -> bool:
        return _has_file(self.home, _PROXY_VAL)

    def proxy_value(self):
        return _get_file_content(os.join(self.home, _PROXY_VAL))

    def proxy_valid(self) -> bool:
        if self.has_proxy():
            value = self.proxy_value()
            os.path.exists(value) and os.path.isdir(value)
            return True
        else:
            return True

    def set_kv(self, key: str, value: str):
        self._set_value(key, value)
    

    def _get_deen_key(self)->str:
        return _EncryptionTools.b64_format(self._get_default_cred())

    def get_kv(self, key: str) -> Optional[str]:
        if self.has_kv(key):
            data = _get_file_content(self._key_value_name(key))
            nonce = _get_file_content(self._key_nonce_name(key))
            tag = _get_file_content(self._key_tag_name(key))
            if data is None or nonce is None or tag is None:
                raise Exception("The data structure is not completed")
            return _EncryptionTools.decrypt_data(self._get_deen_key(), data, nonce, tag)
        else:
            return None
        return _get_kv(self.home, key)
    
    def _set_value(self, key, data: str):
        with open(self._key_value_name(key), "w") as key_file:
            with open(self._key_nonce_name(key), "w") as nonce_file:
                with open(self._key_tag_name(key), "w") as tag_file:
                    ciphertext, nonce, tag = _EncryptionTools.encrypt_data(self._get_default_cred(), data)
                    key_file.write(ciphertext)
                    nonce_file.write(nonce)
                    tag_file.write(tag)
            

    def rm_kv(self, key: str) -> Optional[str]:
        if self.has_kv(key):
            v = self.get_kv(key)
            os.remove(self._key_value_name(key))
            os.remove(self._key_nonce_name(key))
            os.remove(self._key_tag_name(key))
            return v
        else:
            return None
    

    def has_kv(self, key: str) -> Optional[bool]:
        return True if key in self._keys() else False

    def list(self):
        files = list(self._keys())
        var_num = len(files)
        print("Number of variable: %s" % var_num)
        for file in files:
            # print("%s: %s" % (file, self.get_kv(file)))
            print("%s: [hidden]" % (file))
    
    def _key_value_name(self, key: str)->str:
        return join(self.home, f"{key}.kv")

    def _key_nonce_name(self, key: str)->str:
        return join(self.home, f"{key}.kv.nonce")

    def _key_tag_name(self, key: str)->str:
        return join(self.home, f"{key}.kv.tag")

    def _keys(self):
        for filename in os.listdir(self.home):
            if filename.endswith('.kv'):
                yield filename[0:-3]
        

    @staticmethod
    def appDefault(name: str):
        return CustApp(Path.home(), name)
