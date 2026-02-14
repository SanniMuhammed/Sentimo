"""Named entity recognition for crypto assets, people, protocols."""
import re, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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
    "polygon": "Polygon", "matic": "Polygon",
    "litecoin": "Litecoin", "ltc": "Litecoin",
    "uniswap": "Uniswap", "uni": "Uniswap",
    "aave": "Aave",
    "shiba": "Shiba Inu", "shib": "Shiba Inu",
    "pepe": "Pepe",
    "toncoin": "Toncoin", "ton": "Toncoin",
    "tron": "Tron", "trx": "Tron",
    "near": "NEAR", "near protocol": "NEAR",
    "cosmos": "Cosmos", "atom": "Cosmos",
    "aptos": "Aptos", "apt": "Aptos",
    "arbitrum": "Arbitrum", "arb": "Arbitrum",
    "optimism": "Optimism", "op": "Optimism",
    "sui": "Sui",
    "sei": "Sei",
    "render": "Render", "rndr": "Render",
    "injective": "Injective", "inj": "Injective",
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
}

PROTOCOL_MAP = {
    "uniswap": "Uniswap", "aave": "Aave", "lido": "Lido",
    "compound": "Compound", "makerdao": "MakerDAO", "maker": "MakerDAO",
    "curve": "Curve", "raydium": "Raydium", "jupiter": "Jupiter",
    "base": "Base", "arbitrum": "Arbitrum", "optimism": "Optimism",
    "opensea": "OpenSea", "blur": "Blur",
    "pancakeswap": "PancakeSwap", "sushiswap": "SushiSwap",
}

EXCHANGE_MAP = {
    "binance": "Binance", "coinbase": "Coinbase", "kraken": "Kraken",
    "okx": "OKX", "bybit": "Bybit", "kucoin": "KuCoin",
    "bitfinex": "Bitfinex", "gemini": "Gemini", "robinhood": "Robinhood",
}

def _build_pattern(mapping):
    keys = sorted(mapping.keys(), key=len, reverse=True)
    escaped = [re.escape(k) for k in keys]
    return re.compile(r'\b(' + '|'.join(escaped) + r')\b', re.IGNORECASE)

_coin_re = _build_pattern(COIN_MAP)
_person_re = _build_pattern(PERSON_MAP)
_protocol_re = _build_pattern(PROTOCOL_MAP)
_exchange_re = _build_pattern(EXCHANGE_MAP)


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
    return list(results)
