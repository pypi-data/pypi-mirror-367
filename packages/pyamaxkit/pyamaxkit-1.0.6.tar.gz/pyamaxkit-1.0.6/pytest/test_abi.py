from pyamaxkit import amaxapi
def test_pack_unpack_array():
    abi = '''
    {
    "version": "eosio::abi/1.0",
    "types": [],
    "structs": [{
        "name": "sayhello",
        "base": "",
        "fields": [
            {"name":"worlds", "type":"string[]"}
        ]
        }
    ],
    "actions": [{
        "name": "sayhello",
        "type": "sayhello",
        "ricardian_contract": ""
        }
    ],
    "tables": [
    ]
    }
    '''
    amaxapi.set_abi('test', abi)

    args = {'worlds': ['hello', 'world']}
    packed_args = amaxapi.pack_args('test', 'sayhello', args)
    assert packed_args == b'\x02\x05hello\x05world'

    args = amaxapi.unpack_args('test', 'sayhello', packed_args.hex())
    assert args == {"worlds":["hello","world"]}
