import flet as ft

AVAILABLE_ACCOUNT_ICONS = {
    "Wallet": ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
    "Bank": ft.icons.ACCOUNT_BALANCE_OUTLINED,
    "Credit Card": ft.icons.CREDIT_CARD_OUTLINED,
    "Savings": ft.icons.SAVINGS_OUTLINED,
    "Cash": ft.icons.MONEY_OUTLINED,
    "Business": ft.icons.BUSINESS_CENTER_OUTLINED,
    "Investment": ft.icons.TRENDING_UP_OUTLINED,
    "Gift": ft.icons.REDEEM_OUTLINED,
    "Default": ft.icons.WALLET_OUTLINED,
}

def get_icon_by_name(icon_name):
    return AVAILABLE_ACCOUNT_ICONS.get(icon_name, AVAILABLE_ACCOUNT_ICONS["Default"])

def get_icon_names():
    return list(AVAILABLE_ACCOUNT_ICONS.keys())