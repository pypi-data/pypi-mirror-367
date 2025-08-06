import os
os.environ["using-j-vault-rest-server"]="localhost,7910,false,harden"
import py_xh_custapp_xethhung12 as project
from j_vault_http_client_xethhung12 import client
import time
import sys

def main():
    client.load_to_env()
    def show_usage():
        script_str = "python -m pyXhCustApp {name_space}"
        print("%s list #Show all all" % script_str)
        print("%s exist {key} #return true if {key} exists " % script_str)
        print("%s value {key} #return value of {key} or None " % script_str)
        print("%s set {key} {value} #set {value} to {key} " % script_str)
        print("%s remove {key} #remove {key} " % script_str)


    if len(sys.argv) == 1:
        show_usage()
        exit(1)

    name_space = sys.argv[1]
    app = project.CustApp.appDefault(name_space)

    if len(sys.argv) == 2:
        show_usage()
        exit(1)

    cmd = sys.argv[2]
    if len(sys.argv) == 3:
        if cmd == "list":
            app.list()
            exit(0)

    if len(sys.argv) == 3:
        show_usage()
        exit(1)

    key = sys.argv[3]
    if len(sys.argv) == 4:
        if cmd == "exist":
            print("Contains key[%s]: %r" % (key, app.has_kv(key)))
            exit(0)
        if cmd == "value":
            print("%s: %s" % (key, app.get_kv(key)))
            exit(0)
        if cmd == "remove":
            if app.has_kv(key):
                print("Removed %s: %s" % (key, app.rm_kv(key)))
            else:
                print("key[%s] not exists" % key)
            exit(0)
        show_usage()
        exit(1)

    if len(sys.argv) == 5 and cmd == "set":
        value = sys.argv[4]
        app.set_kv(key, value)
        print("set key[%s] as %s" % (key, value))
        exit(0)

    show_usage()
    exit(1)
