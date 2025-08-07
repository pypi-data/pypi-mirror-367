# TrakteerApiWrapper

[![Downloads](https://static.pepy.tech/badge/TrakteerApiWrapper)](https://pepy.tech/project/TrakteerApiWrapper)

Python wrapper untuk Trakteer Public API.  
Mudah digunakan untuk mengambil informasi seperti saldo saat ini, riwayat dukungan, riwayat transaksi, dan total jumlah donasi dari email tertentu.

## 🔗 API Endpoint

Base URL: `https://api.trakteer.id/v1/public`

---

## 🔧 Install

```bash
pip install TrakteerApiWrapper
```

## Usage
```python
from TrakteerApiWrapper import TrakteerApi

trakteer = TrakteerApi("enter_your_api_key_here")

# Get current balance
balance = trakteer.get_current_balance()
print("Balance:", balance)

# Get support history
support_history = trakteer.get_support_history(limit=2, page=1, include=["is_guest", "reply_message", "net_amount", "payment_method", "order_id", "supporter_email", "updated_at_diff_label"])
print("Support History:", support_history)

# Get transaction history
transactions = trakteer.get_transaction_history(limit=2, page=1, include=["is_guest", "reply_message", "net_amount", "updated_at_diff_label"])
print("Transactions:", transactions)

# Get quantity given
quantity = trakteer.get_quantity_given("supporter@example.com")
print("Quantity Given:", quantity)

# please refer to https://trakteer.id/manage/api-trakteer
```
