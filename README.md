## Python SDK for Syncswap

### How to use?
- Swap two tokens
```python
token_pair = {
    'token_in_address': '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91', #WETH
    'pool_address': '0x80115c708E12eDd42E504c1cD52Aea96C547c05c', # WETH - USDC
    'amount': 1 # ETH
}

swap(os.environ['private_key'], token_pair)

```

- Deposit Pool
```python
# WETH is a special version of ETH that has more capabilities. 
# And USDC/ETH and USDC/WETH are the same pool. You can choose either ETH or WETH to collect when withdrawing from the pool.
deposit_params = {
    'pool_address': '0x80115c708E12eDd42E504c1cD52Aea96C547c05c',
    'token_in_amount': int("hex_number", 16),
    'token_in_address': '0x0000000000000000000000000000000000000000', # ETH
    'token_out_amount': int("hex_number", 16),
    'token_out_address': '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4', # USDC
    'min_liquidity': 0,
}

deposit_pool(os.environ['private_key'], deposit_params)


```