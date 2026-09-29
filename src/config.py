"""
This file contains variable information such as ticker list to be fetched.
"""

TICKER_LIST = ["AI", "AIR", "BNP", "CAP", "CA", "BN", "ENGI", "MC", "ML", "ORA"]

MAIN_API_SOURCE = "yfinance"


TICKER_SUFFIXE_LIST = [
    "PA", "AS", "BR", "LS", "MC", "MI", "DE", "F", "BE", "DU", "HM", "MU", "SG",
    "VI", "SW", "L", "IL", "IR", "ST", "HE", "CO", "OL", "IC", "WA", "PR", "BD",
    "AT", "IS", "TA", "TO", "V", "CN", "MX", "SA", "BA", "SN", "HK", "T", "KS",
    "KQ", "SS", "SZ", "TW", "SI", "KL", "JK", "BK", "NS", "BO", "AX", "NZ", "JO",
    "SR", "QA", "KW", "FP",
]

COMPANY_SUFFIXE_LIST = [
    "sa", "sas", "sasu", "sarl", "eurl", "snc", "se",
    "gmbh", "ag", "kg", "ug",
    "ltd", "limited", "plc", "llp", "lp",
    "inc", "incorporated", "corp", "corporation", "co", "company", "llc",
    "bv", "nv", "spa", "srl", "sl", "ab", "oy", "oyj", "as", "aps",
    "pty ltd", "pte ltd", "sdn bhd", "co ltd", "sp z oo", "sa de cv", "sca",
]

SECTOR_MAPPING = {"chimie": "chemicals", "aerospace & defense": "aerospace and defense", "banque": "finance", "services informatiques": "IT services", "distribution alimentaire": "retail", "agroalimentaire": "packaged food", "utilities": "utilities", "luxe": "luxury", "automobile": "car", "telecoms": "telecom", "banking": "finance", "services financiers": "finance"}