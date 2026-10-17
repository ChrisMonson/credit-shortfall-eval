import copy

import pytest

from shortfall.account import Account

ACCOUNT = {
    "firstName": "Dana",
    "lastName": "Whitfield",
    "email": "dana.whitfield@fastmail.com",
    "memberSince": "2024-03-11",
    "planTier": "Standard",
    "timezone": "America/Denver",
    "defaultOutputLanguage": "en-US",
    "notifications": {
        "emailOnCompletion": True,
        "weeklyUsageReport": False,
    },
    "usageHistory": [
        {"month": "2026-08", "creditsPurchased": 2000, "creditsUsed": 1912, "spend": 20.00},
        {"month": "2026-09", "creditsPurchased": 2000, "creditsUsed": 2047, "spend": 20.00},
    ],
    "creditBalance": 117,
    "totalSummarized": 3412,
    "latestSummarizedFile": "Vendor_Contract_Renewal_Notes.txt",
    "autoRecharge": {
        "enabled": False,
        "amount": 5.00,
        "paymentMethod": "Visa ••••4417",
    },
}

FILENAMES = [
    "Annual_Safety_Audit.txt",
    "Board_Minutes_March.txt",
    "Q3_Facilities_Budget_Review.txt",
]


@pytest.fixture
def account_data() -> dict:
    return copy.deepcopy(ACCOUNT)


@pytest.fixture
def account(account_data) -> Account:
    return Account(account_data, FILENAMES)


@pytest.fixture
def make_account():
    """An account with a given balance and auto-recharge setting."""

    def make(balance: int, auto_recharge: bool = False) -> Account:
        data = copy.deepcopy(ACCOUNT)
        data["creditBalance"] = balance
        data["autoRecharge"]["enabled"] = auto_recharge
        return Account(data, FILENAMES)

    return make
