from requests import get
from matplotlib import pyplot as plt
import json
from web3 import Web3
from datetime import datetime
from pandas_datareader import DataReader

ETH_API = "D56Y233GUAWJ2XGF2PBPGGZS4JEZ16KXQA"
API = ETH_API
address = "0x73bceb1cd57c711feac4224d062b0f6ff338501e"

BASE_URL = "https://api.etherscan.io/api"

# create api call url function
def make_api_url(module, action, address, **kwargs):
    url = BASE_URL + f"?module={module}&action={action}&address={address}&apikey={API}"

    for key, value in kwargs.items():
        url += f"&{key}={value}"

    return url


# get eth balance of a certain wallet address function
def get_account_balance(address):
    balance_url = make_api_url("account", "balance", address, tag="latest")
    response = get(balance_url)
    data = response.json()
    balance_eth = Web3.fromWei(int(data["result"]), "ether")
    return balance_eth


# get transaction of an address
def get_transactions(
    address,
):
    # Get external transactions
    transaction_url = make_api_url(
        "account",
        "txlist",
        address,
        startblock=0,
        endblock=99999999,
        page=1,
        offset=10000,
        sort="asc",
        apikey=API,
    )
    response = get(transaction_url)
    data = response.json()["result"]

    # Get internal transactions
    internal_transaction_url = make_api_url(
        "account",
        "txlistinternal",
        address,
        startblock=0,
        endblock=99999999,
        page=1,
        offset=10000,
        sort="asc",
        apikey=API,
    )
    response_internal = get(internal_transaction_url)
    data_internal = response_internal.json()["result"]

    # combining both lists into one
    data.extend(data_internal)
    # sorting the new data list according to the timestemp key of each element
    data.sort(key=lambda x: int(x["timeStamp"]))

    current_balance = 0
    balances = []
    times = []
    counter = 0

    for tx in data:
        block = tx["blockNumber"]
        to = tx["to"]
        from_addr = tx["from"]
        value = Web3.fromWei(int(tx["value"]), "ether")
        if "gasPrice" in tx:
            gas = Web3.fromWei(int(tx["gasUsed"]) * int(tx["gasPrice"]), "ether")
        else:
            gas = Web3.fromWei(int(tx["gasUsed"]), "ether")
        time = datetime.fromtimestamp(int(tx["timeStamp"]))

        money_in = to.lower() == address.lower()
        if money_in:
            current_balance += value
        else:
            current_balance -= value + gas

        balances.append(current_balance)
        times.append(time)

        """
        print(f"{counter}------------------------------")
        counter += 1
        print(f"Block: {block}")
        print(f"From: {from_addr}")
        print(f"To: {to}")
        print(f"Value: {value}")
        print(f"Gas cost: {gas}")
        print(f"Time: {time}")
        """

    plt.plot(times, balances)
    plt.show()
    print(current_balance)


eth_balance = get_account_balance(address)
get_transactions(address)
print(f"Current ETH balance: {eth_balance}")
