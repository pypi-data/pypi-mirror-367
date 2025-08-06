# PyXHCustApp

A library provide functionality process chia plot log.

# Installation

```python_script
pip install pyXhCustApp
```

```python_script
pip3 install pyXhCustApp
```

# Demo

```python
from py_xh_custapp_xethhung12 import CustApp
CustApp.appDefault("abc_app")
print(app.has_proxy())
app.set_kv('xxx', "xxx")
app.set_kv('xxx', "yyy")
print(app.get_kv('xxx'))
app.rm_kv('xxx')
print(app.has_kv('xxx'))
print(app.home)
```

```shell script
# `python -m py_xh_custapp_xethhung12` can be replace by `pyXhCustapp` as short cut script
python -m py_xh_custapp_xethhung12 {name_space} list #Show all all
python -m py_xh_custapp_xethhung12 {name_space} exist {key} #return true if {key} exists
python -m py_xh_custapp_xethhung12 {name_space} value {key} #return value of {key} or None
python -m py_xh_custapp_xethhung12 {name_space} set {key} {value} #set {value} to {key}
python -m py_xh_custapp_xethhung12 {name_space} remove {key} #remove {key}
```
