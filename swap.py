import json
import os

import math
import time
from datetime import datetime

from eth_abi import encode
from eth_account import Account
from web3 import Web3

from pathlib import Path

from const import zero_address, withdraw_return_eth, router_address, rpc

p = Path(__file__).with_name('router.abi')
with open(os.path.join(os.path.dirname(__file__), 'router.abi'), 'r') as f:
    router_abi = json.load(f)

with open(os.path.join(os.path.dirname(__file__), 'erc20.abi'), 'r') as f:
    token_abi = json.load(f)

w3 = Web3(Web3.HTTPProvider(rpc))


def get_account(private_key):
    acc = Account.from_key(private_key)
    return acc


def swap(private_key, pair_token):
    acc = get_account(private_key)

    token_in_address = pair_token['token_in_address']
    pool_address = pair_token['pool_address']
    amount = pair_token['amount']
    swap_amount = int(amount * 10 ** 18)
    caller = acc.address

    encoded_data = encode(["address", "address", "uint8"], [token_in_address, caller, withdraw_return_eth])
    native_address = zero_address
    swap_steps = [
        {
            'pool': pool_address,
            'data': encoded_data,
            'callback': zero_address,
            'callbackData': '0x'
        }
    ]

    paths = [
        {
            'steps': swap_steps,
            'tokenIn': native_address,
            'amountIn': swap_amount
        }
    ]

    # If we want to use the native ETH as the input token,
    # the `tokenIn` on path should be replaced with the zero address.
    # Note: however we still have to encode the wETH address to pool's swap data.

    router = w3.eth.contract(address=router_address, abi=router_abi)
    deadline = math.floor(time.time() + 60 * 30)  # 30s

    tx = router.functions.swap(paths, 0, deadline).build_transaction(
        {
            "from": caller,
            "nonce": w3.eth.get_transaction_count(caller),
            "value": swap_amount,
            "gasPrice": w3.eth.gas_price,
            "gas": 1500000,
        }
    )

    signed_tx = acc.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    tx_url = 'https://explorer.zksync.io/tx/' + tx_hash.hex()
    print("Submit tx successfully" + " => " + tx_url)


def deposit_pool(private_key, params):
    acc = get_account(private_key)
    caller = acc.address

    pool_address = params['pool_address']
    token_in_amount = params['token_in_amount']
    token_out_amount = params['token_out_amount']
    token_in_address = params['token_in_address']
    token_out_address = params['token_out_address']
    min_liquidity = int(params['min_liquidity'])
    pool_factory_address = params['pool_factory_address']

    # unlock token out if you don't approve the maximum amount
    approval_erc20(acc, token_out_address, router_address, token_out_amount)

    # add pool
    token_inputs = [
        (token_in_address, token_in_amount),
        (token_out_address, token_out_amount)
    ]

    router_contract = w3.eth.contract(address=pool_factory_address, abi=router_abi)

    encoded_data = encode(['address'], [caller])

    tx = router_contract.functions.addLiquidity2(
        pool_address,
        token_inputs,
        encoded_data,
        min_liquidity,
        zero_address,
        '0x'
    ).build_transaction(
        {
            "from": caller,
            "nonce": w3.eth.get_transaction_count(caller),
            "value": 0,
            "gasPrice": w3.eth.gas_price,
            "gas": 1500000,
        }
    )
    signed_tx = acc.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)


    tx_url = 'https://explorer.zksync.io/tx/' + tx_hash.hex()
    print("Submit tx successfully" + " => " + tx_url)


def approval_erc20(acc, token_address, spender_address, amount):
    caller = acc.address
    token_contract = w3.eth.contract(address=token_address, abi=token_abi)

    decimal_factor = 10 ** token_contract.functions.decimals().call()
    approved_amount = int(amount * decimal_factor)

    approve_tx = token_contract.functions.approve(spender_address, approved_amount).build_transaction({
        'from': caller,
        'nonce': w3.eth.get_transaction_count(caller),
        'gas': 200000,
        "gasPrice": w3.eth.gas_price,
    })

    # Sign the transaction
    signed_tx = acc.sign_transaction(approve_tx)

    # Send the signed transaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Wait for the transaction to be mined
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Return the transaction receipt
    return receipt
