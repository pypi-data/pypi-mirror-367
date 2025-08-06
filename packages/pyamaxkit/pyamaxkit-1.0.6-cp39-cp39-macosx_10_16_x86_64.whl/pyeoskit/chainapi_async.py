import json
import copy
import time
import base64
import asyncio

from . import config
from . import wallet
from . import defaultabi
from . import wasmcompiler
from . import log
from . import ledger

from .transaction import Transaction
from .chaincache import ChainCache
from .rpc_interface import RPCInterface
from .chainnative import ChainNative
from .exceptions import ChainException
from . import wallet

from typing import Union, Any, Dict, List, Optional

logger = log.get_logger(__name__)


class ChainApiAsync(RPCInterface, ChainNative):
    def __init__(self, node_url = 'http://127.0.0.1:8888', network='EOS'):
        RPCInterface.__init__(self, _async=True)
        ChainNative.__init__(self)

        self.db = ChainCache(self, network)
        self.set_node(node_url)

        self.chain_info: Optional[Dict] = None
        self.chain_id: Optional[str] = None
        self.refresh_time = 0.0

        async def close_async_client():
            try:
                while True:
                    await asyncio.sleep(100000000.0)
            except asyncio.CancelledError:
                if self.async_client:
                    await self.async_client.aclose()
                    self.async_client = None
        asyncio.create_task(close_async_client())

    def enable_decode(self, json_format):
        super().json_decode = json_format

    def init(self):
        self.get_code(config.system_contract)
        self.get_code(config.main_token_contract)

    def set_node(self, url):
        super().set_node(url)
        self.reset_chain_info()

    def reset_chain_info(self):
        self.refresh_time = 0.0
        self.chain_id = 0.0
        self.chain_info = None

    async def refresh_chain_info(self):
        if time.time() < self.refresh_time + 60:
            return self.chain_info

        self.chain_info = await self.get_info()
        self.chain_id = self.chain_info['chain_id']
        self.refresh_time = time.time()
        return self.chain_info

    async def get_chain_id(self):
        return await self.get_info()['chain_id']

    def push_transaction(self, trx: Union[str, dict]):
        return super().push_transaction(trx)

    async def get_required_keys(self, trx, public_keys):
        r = await super().get_required_keys(trx, public_keys)
        return r['required_keys']

    async def get_sign_keys(self, actions, pub_keys):
        fake_tx = {
            "expiration": "2021-09-01T16:15:16",
            "ref_block_num": 20676,
            "ref_block_prefix": 4052960473,
            "max_net_usage_words": 0,
            "max_cpu_usage_ms": 0,
            "delay_sec": 0,
            "context_free_actions": [],
            "actions": [
            ],
            "transaction_extensions": [],
            "signatures": [],
            "context_free_data": []
        }
        for a in actions:
            action = {
                "account": a[0],
                "name": a[1],
                "authorization": [
                ],
                "data": ""
            }
            permissions = a[3]
            for key in permissions:
                action['authorization'].append({
                    "actor": key,
                    "permission": permissions[key]
                })
            fake_tx['actions'].append(action)
        return await self.get_required_keys(json.dumps(fake_tx), pub_keys)

    async def generate_packed_transaction(self, actions, expiration, ref_block, chain_id, compress=0, indices=None):
        fake_actions = []
        for a in actions:
            fake_actions.append([a[0], a[1], '', a[3]])

        if not expiration:
            expiration = int(time.time()) + 3*60
        else:
            expiration = int(time.time()) + expiration

        try:
            tx = Transaction(self.chain_index, expiration, ref_block, chain_id)
            for a in actions:
                contract, action_name, args, permissions = a
                if isinstance(args, bytes):
                    args = args.hex()
                elif isinstance(args, dict):
                    args = json.dumps(args)
                elif isinstance(args, str):
                    pass
                else:
                    tx.free()
                    raise Exception('Invalid args type')

                if isinstance(permissions, dict):
                    _permissions = permissions
                    permissions = []
                    for actor in _permissions:
                        permissions.append({actor: _permissions[actor]})
                permissions = json.dumps(permissions)
                self.check_abi(contract)
                tx.add_action(contract, action_name, args, permissions)

            local_wallet_pub_keys = wallet.get_public_keys()
            available_pub_keys = set(local_wallet_pub_keys)

            ledger_pub_keys = set()
            if not indices is None:
                ledger_pub_keys = ledger.get_public_keys(indices)
                available_pub_keys |= set(ledger_pub_keys)

            required_keys = await self.get_sign_keys(fake_actions, list(available_pub_keys))
            required_keys = set(required_keys)

            signatures = set()
            sign_keys = required_keys & set(local_wallet_pub_keys)
            for key in sign_keys:
                signatures.add(tx.sign(key))

            packed_tx = tx.pack(compress, False)
            sign_keys = required_keys & set(ledger_pub_keys)
            if not sign_keys:
                return packed_tx

            packed_tx = json.loads(packed_tx)
            tx_json = tx.json()
            for key in sign_keys:
                index = indices[ledger_pub_keys.index(key)]
                signs = ledger.sign(tx_json, [index], chain_id)
                signatures |= set(signs)
            packed_tx['signatures'] = list(signatures)
            return json.dumps(packed_tx)
        finally:
            tx.free()

    async def push_action(self, contract, action, args, permissions=None, compress=False, expiration=0, ref_block_id=None, indices=None, payer=None, payer_permission="active"):
        if not permissions:
            permissions = {contract:'active'}
        a = [contract, action, args, permissions]
        return await self.push_actions([a], expiration, compress, ref_block_id, indices, payer=payer, payer_permission=payer_permission)

    async def push_actions(self, actions, expiration=0, compress=0, ref_block_id=None, indices=None, payer=None, payer_permission="active"):
        if payer:
            action = [payer, 'noop', b'', {payer: payer_permission}]
            actions.insert(0, action)
        try:
            chain_info = None
            if not self.chain_id or not ref_block_id:
                chain_info = await self.refresh_chain_info()
                if not self.chain_id:
                    self.chain_id = chain_info['chain_id']
                if not ref_block_id:
                    ref_block_id = chain_info['last_irreversible_block_id']
            tx = await self.generate_packed_transaction(actions, expiration, ref_block_id, self.chain_id, compress, indices=indices)
            return await super().push_transaction(tx)
        except Exception as e:
            raise e
        finally:
            ledger.close_dongle()

    async def push_transactions(self, aaa, expiration=60, compress=False, indices=None):
        chain_info = await self.refresh_chain_info()
        ref_block = chain_info['last_irreversible_block_id']
        chain_id = chain_info['chain_id']

        txs = []
        for aa in aaa:
            tx = await self.generate_packed_transaction(aa, expiration, ref_block, chain_id, compress, indices=indices)
            txs.append(tx)
        return await super().push_transactions(txs)

    def strip_prefix(self, pub_key):
        prefixes = {'EOS', 'AM', config.public_key_prefix}
        for p in prefixes:
            if pub_key.startswith(p):
                return pub_key[len(p):]
        return pub_key

    async def get_account(self, account):
        if not self.s2n(account):
            return None
            raise ChainException('Invalid account name')
        try:
            return await super().get_account(account)
        except ChainException as e:
            if e.json and e.json['error']['details'][0]['message'].startswith('unknown key'):
                return None
            raise e

    async def create_account(self, creator, account, owner_key, active_key, ram_bytes=0, stake_net=0.0, stake_cpu=0.0, sign=True, indices=None):
        actions = []
        args = {
            'creator': creator,
            'name': account,
            'owner': {
                'threshold': 1,
                'keys': [{'key': owner_key, 'weight': 1}],
                'accounts': [],
                'waits': []
            },
            'active': {
                'threshold': 1,
                'keys': [{'key': active_key, 'weight': 1}],
                'accounts': [],
                'waits': []
            }
        }
        args = self.pack_args(config.system_contract, 'newaccount', args)
        act = [config.system_contract, 'newaccount', args, {creator:'active'}]
        actions.append(act)

        if ram_bytes:
            args = {'payer':creator, 'receiver':account, 'bytes':ram_bytes}
            args = self.pack_args(config.system_contract, 'buyrambytes', args)
            act = [config.system_contract, 'buyrambytes', args, {creator:'active'}]
            actions.append(act)

        if stake_net or stake_cpu:
            args = {
                'from': creator,
                'receiver': account,
                'stake_net_quantity': '%0.4f %s'%(stake_net, config.main_token),
                'stake_cpu_quantity': '%0.4f %s'%(stake_cpu, config.main_token),
                'transfer': 1
            }
            args = self.pack_args(config.system_contract, 'delegatebw', args)
            act = [config.system_contract, 'delegatebw', args, {creator:'active'}]
            actions.append(act)
        return self.push_actions(actions, indices=indices)

    async def get_balance(self, account, token_account=None, token_name=None):
        if not token_name:
            token_name = config.main_token

        if not token_account:
            token_account = config.main_token_contract

        if not token_name:
            token_name = config.main_token

        try:
            ret = await super().get_currency_balance(token_account, account, token_name)
            if ret:
                return float(ret[0].split(' ')[0])
        except Exception as e:
            return 0.0
        return 0.0

    async def transfer(self, _from, to, amount, memo='', token_account=None, token_name=None, token_precision=4, permission='active', indices=None, payer=None, payer_permission="active"):
        if not token_account:
            token_account = config.main_token_contract
        if not token_name:
            token_name = config.main_token
        args = {"from":_from, "to": to, "quantity": f'%.{token_precision}f %s'%(amount, token_name), "memo":memo}
        return await self.push_action(token_account, 'transfer', args, {_from:permission}, indices=indices, payer=payer, payer_permission=payer_permission)

    async def get_code(self, account):
        code = self.db.get_code(account)
        if code:
            return code

        try:
            code = await super().get_code(account)
            code = base64.b64decode(code['wasm'])
            self.db.set_code(account, code)
            return code
        except Exception as e:
            return None

    async def get_raw_code(self, account):
        try:
            code = await super().get_code(account)
            return code
        except Exception as e:
            return None

    def set_code(self, account, code):
        self.db.set_code(account, code)

    def set_abi(self, account, abi):
        super().set_abi(self.chain_index, account, abi)
        self.db.set_abi(account, abi)

    async def get_abi(self, account):
        if account == config.main_token_contract:
            return defaultabi.eosio_token_abi
        elif account == config.system_contract:
            if config.main_token in defaultabi.eosio_system_abi:
                return defaultabi.eosio_system_abi[config.main_token]
            else:
                return defaultabi.eosio_system_abi['EOS']

        abi = self.db.get_abi(account)
        if abi:
            return abi

        abi = await super().get_abi(account)
        if abi and 'abi' in abi:
            abi = json.dumps(abi['abi'])
            self.set_abi(account, abi)
        else:
            abi = ''
            self.set_abi(account, abi)
        return abi

    async def deploy_contract(self, account, code, abi, vm_type=0, vm_version=0, sign=True, compress=False, indices=None, payer=None, payer_permission="active"):
        if vm_type == 0:
            return await self.deploy_wasm_contract(account, code, abi, vm_type, vm_version, sign, compress, indices=indices, payer=payer, payer_permission=payer_permission)
        elif vm_type == 1:
            return await self.deploy_python_contract(account, code, abi, indices=indices)
        else:
            raise Exception(f'Unknown vm type {vm_type}')

    async def deploy_wasm_contract(self, account, code, abi, vm_type=0, vm_version=0, sign=True, compress=0, indices=None, payer=None, payer_permission="active"):
        origin_abi = abi
        actions = []
        setcode = {"account":account,
                "vmtype":vm_type,
                "vmversion":vm_version,
                "code":code.hex()
        }
        setcode = self.pack_args(config.system_contract, 'setcode', setcode)
        setcode = [config.system_contract, 'setcode', setcode, {account:'active'}]
        actions.append(setcode)

        if abi:
            if isinstance(abi, dict):
                abi = json.dumps(abi)
            abi = self.pack_abi(self.chain_index, abi)
            assert abi
        else:
            abi = b''
        setabi = self.pack_args(config.system_contract, 'setabi', {'account':account, 'abi':abi.hex()})
        setabi = [config.system_contract, 'setabi', setabi, {account:'active'}]
        actions.append(setabi)

        ret = await self.push_actions(actions, compress, indices=indices, payer=payer, payer_permission=payer_permission)
        if 'error' in ret:
            raise Exception(ret['error'])

        self.set_abi(account, origin_abi)

        return ret

    async def deploy_code(self, account, code, vm_type=0, vm_version=0, indices=None, payer=None, payer_permission="active"):
        setcode = {"account":account,
                "vmtype":vm_type,
                "vmversion":vm_version,
                "code":code.hex()
                }
        setcode = self.pack_args(config.system_contract, 'setcode', setcode)
        ret = await self.push_action(config.system_contract, 'setcode', setcode, {account:'active'}, indices=indices, payer=payer, payer_permission=payer_permission)
        self.db.remove_code(account)
        return ret

    async def deploy_abi(self, account, abi, indices=None, payer=None, payer_permission="active"):
        if isinstance(abi, dict):
            abi = json.dumps(abi)

        abi = self.pack_abi(self.chain_index, abi)
        setabi = self.pack_args(config.system_contract, 'setabi', {'account':account, 'abi':abi.hex()})    
        ret = await self.push_action(config.system_contract, 'setabi', setabi, {account:'active'}, indices=indices, payer=payer, payer_permission=payer_permission)
        self.db.remove_abi(account)
        self.clear_abi_cache(self.chain_index, account)
        return ret


    async def deploy_python_contract(self, account, code, abi, deploy_type=0, indices=None):
        '''Deploy a python contract to EOSIO based network
        Args:
            deploy_type (int) : 0 for UUOS network, 1 for EOS network
        '''
        actions = []
        origin_abi = abi
        if config.contract_deploy_type == 0:
            setcode = {
                "account": account,
                "vmtype": 1,
                "vmversion": 0,
                "code":b'python contract'.hex()
            }
            setcode = self.pack_args(config.system_contract, 'setcode', setcode)
            try:
                await self.push_action(config.system_contract, 'setcode', setcode, {account:'active'})
            except Exception as e:
                assert e.json['error']['what'] == "Contract is already running this version of code"

            abi = self.pack_abi(self.chain_index, abi)
            if abi:
                setabi = self.pack_args(config.system_contract, 'setabi', {'account':account, 'abi':abi.hex()})
                setabi = [config.system_contract, 'setabi', setabi, {account:'active'}]
                actions.append(setabi)

            args = self.s2b(account) + code
            setcode = [account, 'setcode', args, {account:'active'}]
            actions.append(setcode)

        elif config.contract_deploy_type == 1:
            python_contract = config.python_contract

            args = self.s2b(account) + code
            setcode = [python_contract, 'setcode', args, {account:'active'}]
            actions.append(setcode)

            abi = self.pack_abi(self.chain_index, abi)
            if abi:
                setabi = self.s2b(account) + abi
                setabi = [python_contract, 'setabi', setabi, {account:'active'}]
                actions.append(setabi)
        else:
            assert 0

        ret = None
        if actions:
            ret = await self.push_actions(actions, indices=indices)

        self.set_abi(account, origin_abi)
        return ret

    async def deploy_python_code(self, account, code, deploy_type=0):
        return await self.deploy_python_contract(account, code, b'', deploy_type)

    async def deploy_module(self, account, module_name, code, deploy_type=1):
        args = self.s2b(account) + self.s2b(module_name) + code
        if deploy_type == 0:
            contract = account
        else:
            contract = config.python_contract

        return await self.push_action(contract, 'setmodule', args, {account:'active'})

    async def exec(self, account, args, permissions = {}):
        if isinstance(args, str):
            args = args.encode('utf8')

        if not isinstance(args, bytes):
            args = str(args)
            args = args.encode('utf8')
        
        if not permissions:
            permissions = {account: 'active'}

        args = self.s2b(account) + args
        if config.contract_deploy_type == 1:
            return await self.push_action(config.python_contract, 'exec', args, permissions)
        else:
            return await self.push_action(account, 'exec', args, permissions)
