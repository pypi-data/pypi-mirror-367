# Transaction

> Auto-generated documentation for [pysrc.transaction](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py) module.

- [Pyeoskit](../README.md#pyeoskit-index) / [Modules](../MODULES.md#pyeoskit-modules) / [Pysrc](index.md#pysrc) / Transaction
    - [Transaction](#transaction)
        - [Transaction().add_action](#transactionadd_action)
        - [Transaction().digest](#transactiondigest)
        - [Transaction().free](#transactionfree)
        - [Transaction.from_json](#transactionfrom_json)
        - [Transaction().json](#transactionjson)
        - [Transaction().marshal](#transactionmarshal)
        - [Transaction().pack](#transactionpack)
        - [Transaction().set_chain_id](#transactionset_chain_id)
        - [Transaction().sign](#transactionsign)
        - [Transaction().sign_by_private_key](#transactionsign_by_private_key)
        - [Transaction.unpack](#transactionunpack)

## Transaction

[[find in source code]](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py#L5)

```python
class Transaction(object):
    def __init__(expiration=0, ref_block=None, chain_id=None):
```

### Transaction().add_action

[[find in source code]](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py#L30)

```python
def add_action(contract, action, args, permissions):
```

### Transaction().digest

[[find in source code]](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py#L41)

```python
def digest(chainId):
```

### Transaction().free

[[find in source code]](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py#L82)

```python
def free():
```

### Transaction.from_json

[[find in source code]](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py#L12)

```python
@staticmethod
def from_json(tx, chain_id=None):
```

### Transaction().json

[[find in source code]](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py#L79)

```python
def json():
```

### Transaction().marshal

[[find in source code]](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py#L71)

```python
def marshal():
```

### Transaction().pack

[[find in source code]](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py#L55)

```python
def pack(compress=False, load=False):
```

### Transaction().set_chain_id

[[find in source code]](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py#L26)

```python
def set_chain_id(chain_id):
```

### Transaction().sign

[[find in source code]](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py#L34)

```python
def sign(pub_key):
```

### Transaction().sign_by_private_key

[[find in source code]](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py#L48)

```python
def sign_by_private_key(priv_key):
```

### Transaction.unpack

[[find in source code]](https://github.com/AMAX-DAO-DEV/pyamaxkit/blob/master/pysrc/transaction.py#L65)

```python
@staticmethod
def unpack(tx):
```
