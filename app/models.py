from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

# ---------- Safe converters ----------
def parse_float(value):
    try:
        return float(value)
    except:
        return None

def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except:
        try:
            return datetime.fromisoformat(value)
        except:
            return None

def clean_str(value):
    if value is None:
        return ""
    return str(value).strip().lower()


# ---------- Trade Dataclass ----------
@dataclass
class Trade:
    trade_id: str
    trade_date: Optional[datetime]
    amount: Optional[float]
    currency: str
    counterparty: str
    instrument: str
    source: str  # "A" or "B"

    def to_dict(self):
        return {
            "trade_id": self.trade_id,
            "trade_date": self.trade_date.isoformat() if self.trade_date else None,
            "amount": self.amount,
            "currency": self.currency,
            "counterparty": self.counterparty,
            "instrument": self.instrument,
            "source": self.source
        }


# ---------- Convert DataFrame Row → Trade object ----------
def row_to_trade(row: Dict[str, Any], source: str) -> Trade:
    return Trade(
        trade_id=str(row.get("trade_id", "")).strip(),
        trade_date=parse_date(str(row.get("trade_date"))),
        amount=parse_float(row.get("amount")),
        currency=clean_str(row.get("currency")).upper(),
        counterparty=clean_str(row.get("counterparty")),
        instrument=clean_str(row.get("instrument")),
        source=source
    )
