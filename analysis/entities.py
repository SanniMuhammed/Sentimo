"""Named entity recognition for crypto assets, people, protocols, regulators."""
import re, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 80+ coins including DeFi protocols, L2s, DEXes
COIN_MAP = {
    "bitcoin": "Bitcoin", "btc": "Bitcoin",
    "ethereum": "Ethereum", "eth": "Ethereum", "ether": "Ethereum",
    "solana": "Solana", "sol": "Solana",
    "cardano": "Cardano", "ada": "Cardano",
    "dogecoin": "Dogecoin", "doge": "Dogecoin",
    "xrp": "XRP", "ripple": "XRP",
    "polkadot": "Polkadot", "dot": "Polkadot",
    "avalanche": "Avalanche", "avax": "Avalanche",
    "chainlink": "Chainlink", "link": "Chainlink",
    "polygon": "Polygon", "matic": "Polygon", "pol": "Polygon",
    "litecoin": "Litecoin", "ltc": "Litecoin",
    "shiba": "Shiba Inu", "shib": "Shiba Inu",
    "pepe": "Pepe",
    "toncoin": "Toncoin", "ton": "Toncoin",
    "tron": "Tron", "trx": "Tron",
    "near": "NEAR", "near protocol": "NEAR",
    "cosmos": "Cosmos", "atom": "Cosmos",
    "aptos": "Aptos", "apt": "Aptos",
    "sui": "Sui",
    "sei": "Sei",
    "render": "Render", "rndr": "Render",
    "injective": "Injective", "inj": "Injective",
    "bonk": "Bonk",
    "wif": "dogwifhat",
    "floki": "Floki",
    "kaspa": "Kaspa", "kas": "Kaspa",
    "celestia": "Celestia", "tia": "Celestia",
    "stacks": "Stacks", "stx": "Stacks",
    "mantle": "Mantle", "mnt": "Mantle",
    "immutable": "Immutable X", "imx": "Immutable X",
    "fetch": "Fetch.ai", "fet": "Fetch.ai",
    "filecoin": "Filecoin", "fil": "Filecoin",
    "algorand": "Algorand", "algo": "Algorand",
    "vechain": "VeChain", "vet": "VeChain",
    "hedera": "Hedera", "hbar": "Hedera",
    "fantom": "Fantom", "ftm": "Fantom",
    "theta": "Theta", "theta network": "Theta",
    "helium": "Helium", "hnt": "Helium",
    "worldcoin": "Worldcoin", "wld": "Worldcoin",
    "ondo": "Ondo", "ondo finance": "Ondo",
    "pyth": "Pyth Network", "pyth network": "Pyth Network",
    "jup": "Jupiter Token",
    "pendle": "Pendle",
    "ethena": "Ethena", "ena": "Ethena",
    "eigen": "EigenLayer", "eigenlayer": "EigenLayer",
    "blast": "Blast",
    "zksync": "zkSync", "zk sync": "zkSync",
    "starknet": "StarkNet", "strk": "StarkNet",
    "manta": "Manta Network",
    "bittensor": "Bittensor", "tao": "Bittensor",
    "akash": "Akash", "akt": "Akash",
    "arweave": "Arweave", "ar": "Arweave",
    "bnb": "BNB", "binance coin": "BNB",
    "usdt": "Tether", "tether": "Tether",
    "usdc": "USD Coin",
    "dai": "DAI",
    "aave": "Aave",
    "uniswap": "Uniswap", "uni": "Uniswap",
    "maker": "Maker", "mkr": "Maker",
    "lido": "Lido", "ldo": "Lido",
    "rune": "THORChain", "thorchain": "THORChain",
}

PERSON_MAP = {
    "vitalik": "Vitalik Buterin", "vitalik buterin": "Vitalik Buterin",
    "cz": "CZ", "changpeng zhao": "CZ",
    "brian armstrong": "Brian Armstrong",
    "gary gensler": "Gary Gensler", "gensler": "Gary Gensler",
    "michael saylor": "Michael Saylor", "saylor": "Michael Saylor",
    "elon musk": "Elon Musk", "elon": "Elon Musk", "musk": "Elon Musk",
    "sbf": "Sam Bankman-Fried", "sam bankman-fried": "Sam Bankman-Fried",
    "do kwon": "Do Kwon",
    "charles hoskinson": "Charles Hoskinson", "hoskinson": "Charles Hoskinson",
    "larry fink": "Larry Fink", "fink": "Larry Fink",
    "cathie wood": "Cathie Wood",
    "jack dorsey": "Jack Dorsey",
    "satoshi": "Satoshi Nakamoto", "satoshi nakamoto": "Satoshi Nakamoto",
    "paolo ardoino": "Paolo Ardoino",
    "brad garlinghouse": "Brad Garlinghouse", "garlinghouse": "Brad Garlinghouse",
    "sam altman": "Sam Altman",
    "justin sun": "Justin Sun",
    "richard heart": "Richard Heart",
    "hayden adams": "Hayden Adams",
    "anatoly yakovenko": "Anatoly Yakovenko", "anatoly": "Anatoly Yakovenko",
    "raj gokal": "Raj Gokal",
}

PROTOCOL_MAP = {
    "uniswap": "Uniswap", "aave": "Aave", "lido": "Lido",
    "compound": "Compound", "makerdao": "MakerDAO", "maker": "MakerDAO",
    "curve": "Curve", "raydium": "Raydium", "jupiter": "Jupiter",
    "base": "Base", "arbitrum": "Arbitrum", "optimism": "Optimism",
    "opensea": "OpenSea", "blur": "Blur",
    "pancakeswap": "PancakeSwap", "sushiswap": "SushiSwap",
    "gmx": "GMX", "dydx": "dYdX",
    "eigenlayer": "EigenLayer", "eigen": "EigenLayer",
    "ethena": "Ethena", "pendle": "Pendle",
    "morpho": "Morpho", "convex": "Convex",
    "yearn": "Yearn", "balancer": "Balancer",
    "1inch": "1inch", "paraswap": "ParaSwap",
    "orca": "Orca", "marinade": "Marinade",
    "jito": "Jito", "tensor": "Tensor",
    "zksync": "zkSync", "starknet": "StarkNet",
    "scroll": "Scroll", "linea": "Linea",
    "blast": "Blast", "mode": "Mode",
    "celestia": "Celestia", "manta": "Manta",
    "layerzero": "LayerZero", "wormhole": "Wormhole",
    "chainlink ccip": "Chainlink CCIP",
    "pyth": "Pyth", "switchboard": "Switchboard",
}

EXCHANGE_MAP = {
    "binance": "Binance", "coinbase": "Coinbase", "kraken": "Kraken",
    "okx": "OKX", "bybit": "Bybit", "kucoin": "KuCoin",
    "bitfinex": "Bitfinex", "gemini": "Gemini", "robinhood": "Robinhood",
    "crypto.com": "Crypto.com", "htx": "HTX", "bitget": "Bitget",
    "mexc": "MEXC", "gate.io": "Gate.io",
}

# Regulatory bodies
REGULATOR_MAP = {
    "sec": "SEC", "securities and exchange commission": "SEC",
    "cftc": "CFTC", "commodity futures trading commission": "CFTC",
    "mica": "MiCA", "markets in crypto-assets": "MiCA",
    "fed": "Federal Reserve", "federal reserve": "Federal Reserve",
    "doj": "DOJ", "department of justice": "DOJ",
    "finra": "FINRA",
    "occ": "OCC",
    "fsb": "FSB", "financial stability board": "FSB",
    "fatf": "FATF",
}


def _build_pattern(mapping):
    keys = sorted(mapping.keys(), key=len, reverse=True)
    escaped = [re.escape(k) for k in keys]
    return re.compile(r'\b(' + '|'.join(escaped) + r')\b', re.IGNORECASE)

_coin_re = _build_pattern(COIN_MAP)
_person_re = _build_pattern(PERSON_MAP)
_protocol_re = _build_pattern(PROTOCOL_MAP)
_exchange_re = _build_pattern(EXCHANGE_MAP)
_regulator_re = _build_pattern(REGULATOR_MAP)


def extract(text: str) -> list:
    """Return list of (entity_name, entity_type) tuples."""
    if not text:
        return []
    results = set()
    for m in _coin_re.finditer(text):
        results.add((COIN_MAP[m.group().lower()], "coin"))
    for m in _person_re.finditer(text):
        results.add((PERSON_MAP[m.group().lower()], "person"))
    for m in _protocol_re.finditer(text):
        results.add((PROTOCOL_MAP[m.group().lower()], "protocol"))
    for m in _exchange_re.finditer(text):
        results.add((EXCHANGE_MAP[m.group().lower()], "exchange"))
    for m in _regulator_re.finditer(text):
        results.add((REGULATOR_MAP[m.group().lower()], "regulator"))
    return list(results)


def extract_cooccurrences(text: str) -> list:
    """Return list of (entity1, entity2) co-occurrence pairs."""
    entities = extract(text)
    pairs = []
    names = [e[0] for e in entities]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            pairs.append(tuple(sorted([names[i], names[j]])))
    return pairs
