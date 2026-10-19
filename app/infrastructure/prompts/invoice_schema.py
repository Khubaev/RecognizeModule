"""Формальная JSON Schema счёта на оплату для режима response_format."""

_STRING = {"type": ["string", "null"]}
_NUMBER = {"type": ["number", "null"]}


def _object(properties: dict, required: list[str]) -> dict:
    """Объект JSON Schema без дополнительных полей."""
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required,
    }


_SIGNATURE = _object(
    {
        "position": {"type": "string"},
        "name": _STRING,
        "signed": {"type": "boolean"},
    },
    ["position", "name", "signed"],
)

_ITEM = _object(
    {
        "row_number": {"type": "integer"},
        "name": {"type": "string"},
        "quantity": {"type": "number"},
        "uom": {"type": "string"},
        "price_rub": {"type": "number"},
        "price_rub_with_vat": _NUMBER,
        "amount_rub": {"type": "number"},
        "amount_rub_with_vat": _NUMBER,
    },
    [
        "row_number",
        "name",
        "quantity",
        "uom",
        "price_rub",
        "price_rub_with_vat",
        "amount_rub",
        "amount_rub_with_vat",
    ],
)

INVOICE_JSON_SCHEMA = _object(
    {
        "document_type": {"type": "string"},
        "document_number": _STRING,
        "document_date": _STRING,
        "payment_deadline": _STRING,
        "bank_details": _object(
            {
                "bank_name": _STRING,
                "bik": _STRING,
                "correspondent_account": _STRING,
                "beneficiary_name": _STRING,
                "beneficiary_inn": _STRING,
                "beneficiary_kpp": _STRING,
                "checking_account": _STRING,
            },
            [
                "bank_name",
                "bik",
                "correspondent_account",
                "beneficiary_name",
                "beneficiary_inn",
                "beneficiary_kpp",
                "checking_account",
            ],
        ),
        "basis": _object(
            {
                "raw": _STRING,
                "contract_number": _STRING,
                "contract_date": _STRING,
            },
            ["raw", "contract_number", "contract_date"],
        ),
        "supplier": _object(
            {
                "name": _STRING,
                "inn": _STRING,
                "kpp": _STRING,
                "address": _STRING,
                "phone": _STRING,
            },
            ["name", "inn", "kpp", "address", "phone"],
        ),
        "buyer": _object(
            {
                "name": _STRING,
                "inn": _STRING,
                "kpp": _STRING,
                "address": _STRING,
            },
            ["name", "inn", "kpp", "address"],
        ),
        "items": {"type": "array", "items": _ITEM},
        "totals": _object(
            {
                "subtotal_without_vat": _NUMBER,
                "vat_rate_percent": _NUMBER,
                "vat_amount": _NUMBER,
                "total_with_vat": _NUMBER,
                "items_count": {"type": ["integer", "null"]},
                "total_amount_in_words": _STRING,
                "amount_in_words": _STRING,
            },
            [
                "subtotal_without_vat",
                "vat_rate_percent",
                "vat_amount",
                "total_with_vat",
                "items_count",
                "total_amount_in_words",
                "amount_in_words",
            ],
        ),
        "payment_terms": _object(
            {
                "raw": _STRING,
                "payment_deadline_text": _STRING,
            },
            ["raw", "payment_deadline_text"],
        ),
        "signatures": _object(
            {
                "manager": _SIGNATURE,
                "chief_accountant": _SIGNATURE,
            },
            ["manager", "chief_accountant"],
        ),
        "extraction_quality": _object(
            {
                "overall_confidence": {"type": "number"},
                "low_confidence_fields": {"type": "array", "items": {"type": "string"}},
                "warnings": {"type": "array", "items": {"type": "string"}},
            },
            ["overall_confidence", "low_confidence_fields", "warnings"],
        ),
    },
    [
        "document_type",
        "document_number",
        "document_date",
        "payment_deadline",
        "bank_details",
        "basis",
        "supplier",
        "buyer",
        "items",
        "totals",
        "payment_terms",
        "signatures",
        "extraction_quality",
    ],
)
