# import os
# os.environ["using-j-vault-rest-server"]="localhost,7910,false,harden"
import py_xh_custapp_xethhung12 as project
from j_vault_http_client_xethhung12 import client
import sys
import argparse




def main():
    client.load_to_env()

    parser = argparse.ArgumentParser(
                    prog='pyXhCustapp',
                    description='A app help manage local py apps',
                    # epilog='Text at the bottom of help'
                    )
    parser.add_argument("--name", "-n", required=True, type=str, default=None, help="The name of the app")

    sub_parsers = parser.add_subparsers(dest="mainCmd")
    sub_cmd = sub_parsers.add_parser("list", help="listing all the configuration of select app")

    sub_cmd = sub_parsers.add_parser("exists", help="check if key of config exists in app")
    sub_cmd.add_argument("--key", "-k", required=True, type=str, help="The key of config to be set in the app")

    sub_cmd = sub_parsers.add_parser("show", help="show the value of select config key in app")
    sub_cmd.add_argument("--key", "-k", required=True, type=str, help="The key of config to be set in the app")

    sub_cmd = sub_parsers.add_parser("set", help="set the config key and vaule in app")
    sub_cmd.add_argument("--key", "-k", required=True, type=str, help="The key of config to be set in the app")
    sub_cmd.add_argument("--value", "-v", required=True, type=str, help="The value of the  config to be set in app")

    sub_cmd = sub_parsers.add_parser("unset", help="unset a config key in app")
    sub_cmd.add_argument("--key", "-k", required=True, type=str, help="The key of config to be set in the app")

    data = parser.parse_args()

    app = project.CustApp.appDefault(data.name)
    
    if data.mainCmd == "list":
        app.list()
    elif data.mainCmd == "exists":
        key=data.key
        print("Contains key[%s]: %r" % (key, app.has_kv(key)))
    elif data.mainCmd == "exists":
        key=data.key
        print("Contains key[%s]: %r" % (key, app.has_kv(key)))
    elif data.mainCmd == "show":
        key=data.key
        print("%s: %s" % (key, app.get_kv(key)))
    elif data.mainCmd == "set":
        key=data.key
        value=data.value
        app.set_kv(key, value)
        print("set key[%s] as %s" % (key, value))
    elif data.mainCmd == "unset":
        key=data.key
        if app.has_kv(key):
            print("Removed %s: %s" % (key, app.rm_kv(key)))
        else:
            print("key[%s] not exists" % key)
    else:
        raise Exception(f"No any match cmd args found: {sys.argv}")
