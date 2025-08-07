# rhea-sdk

[![PyPi Package Version](https://img.shields.io/pypi/v/rhea-sdk?style=flat-square)](https://pypi.org/project/rhea-sdk)
[![Supported python versions](https://img.shields.io/pypi/pyversions/rhea-sdk)](https://pypi.python.org/pypi/rhea-sdk)
[![Twitter](https://img.shields.io/twitter/follow/p_volnov?label=Follow)](https://twitter.com/MaksimA30)

[//]: # ([![downloads]&#40;https://img.shields.io/github/downloads/MaximAntsiferov/rhea-sdk/total?style=flat-square&#41;]&#40;https://pypi.org/project/rhea-sdk&#41;)


**rhea-sdk** is an asynchronous SDK for interacting with Rhea Finance DEX.  
It is made on top of [py-near](https://github.com/pvolnov/py-near) - a pretty simple and fully asynchronous framework for working with NEAR blockchain.
## Examples
<details>
  <summary>📚 Click to see some basic examples</summary>


**Few steps before getting started...**
- Install the latest stable version of rhea-sdk, simply running `pip install rhea-sdk`
- Create NEAR account and get your private key [wallet](https://wallet.near.org/create)

### Usage examples

```python
from py_near.account import Account
from rhea_sdk import Rhea

wnear_contract = "wrap.near"
usdc_contract = "17208628f84f5d6ad33f0da3bbbeb27ffcb398eac501a31bd6ad2011e36133a1"


async def main():
   account = Account(account_id="example.near", private_key="ed25519:...")
   await account.startup()
   
   rhea = Rhea(account=account)

   # Get account tokens balance
   near_balance = await rhea.get_near_balance()
   usdc_balance = await rhea.get_token_balance(usdc_contract)
   wnear_balance = await rhea.get_token_balance(wnear_contract)

   # Wrap or Unwrap some NEAR
   await rhea.wrap_near(0.15)
   await rhea.unwrap_near(0.05)

   # List all DLC pools
   pools = await rhea.dcl.get_pools()

   # Get DLC pool_id by tokens and commission
   pool_id = rhea.dcl.get_pool_id(wnear_contract, usdc_contract, 100)

   # Get pool extended info by pool_id
   pool = await rhea.dcl.get_pool(pool_id)
    
   # Get current tokens price in the pool
   prices = await rhea.dcl.get_tokens_price(pool_id)
   
   # Quote output amount of token for swap
   amount_to_swap = "0.1"
   output_amount = await rhea.dcl.quote(usdc_contract, wnear_contract, pool_id, amount_to_swap)
   
   # Quote input amount of token for swap
   desired_output_amount = "0.1"
   input_amount = await rhea.dcl.quote_by_output(wnear_contract, usdc_contract, pool_id, desired_output_amount)
   
   # Swap
   amount_to_swap = "0.1"
   await rhea.dcl.swap(wnear_contract, usdc_contract, pool_id, amount_to_swap)

   # Swap by output
   desired_output_amount = "0.1"
   max_input_amount = "0.5"
   await rhea.dcl.swap_by_output(wnear_contract, usdc_contract, pool_id, desired_output_amount, max_input_amount)

```

</details>


## Official rhea-sdk resources:
 - Social media:
   - 🇺🇸 [Telegram](https://t.me/maksim30)
   - 🇺🇸 [Twitter](https://twitter.com/MaksimA30)
 - PyPI: [rhea-sdk](https://pypi.python.org/pypi/rhea-sdk)
 - Documentation: [Github repo](https://github.com/MaximAntsiferov/rhea-sdk)
 - Source: [Github repo](https://github.com/MaximAntsiferov/rhea-sdk)
 - Issues/Bug tracker: [Github issues tracker](https://github.com/MaximAntsiferov/rhea-sdk/issues)

## Contributors

### Code Contributors

This project exists thanks to all the people who contribute.
<a href="https://github.com/MaximAntsiferov/rhea-sdk/graphs/contributors"><img src="https://opencollective.com/rhea-sdk/contributors.svg?width=890&button=false" /></a>
