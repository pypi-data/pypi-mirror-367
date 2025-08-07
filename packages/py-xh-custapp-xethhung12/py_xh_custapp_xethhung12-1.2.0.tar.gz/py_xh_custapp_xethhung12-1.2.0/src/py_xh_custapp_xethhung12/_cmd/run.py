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
    parser.add_argument("--name", "-n", required=True, type=str, help="The name of the app")
    parser.add_argument("--profile", "-p", required=False, default=None, type=str, help="The profile to use")

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

    profile = project.Profile(data.profile) if data.profile is not None else None

    app = project.CustApp.appDefault(data.name)
    
    if data.mainCmd == "list":
        app.list(prefix= None if profile is None else profile.as_prefix())
    elif data.mainCmd == "exists":
        key=data.key
        nkey = profile.of_key(key) if profile is not None  else key

        p_str = "" if profile is None else profile.name
        print(f"[{p_str} - {key}] {'not exists' if app.has_kv(nkey) else 'exists'}")
    elif data.mainCmd == "show":
        key=data.key
        nkey = profile.of_key(key) if profile is not None  else key
        p_str = "" if profile is None else profile.name
        print(f"[{p_str} - {key}]: {app.get_kv(nkey)}")
    elif data.mainCmd == "set":
        key=data.key
        value=data.value
        nkey = profile.of_key(key) if profile is not None  else key
        p_str = "" if profile is None else profile.name
        app.set_kv(nkey, value)
        print(f"set [{p_str} - {key}] as {value}")
    elif data.mainCmd == "unset":
        key=data.key
        nkey = profile.of_key(key) if profile is not None  else key
        p_str = "" if profile is None else profile.name
        if app.has_kv(nkey):
            app.rm_kv(nkey)
            print(f"Removed [{p_str} - {key}]")
        else:
            print(f"key[{p_str} - {key}] not exists")
    else:
        raise Exception(f"No any match cmd args found: {sys.argv}")
