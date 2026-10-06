from pydantic import BaseModel, Field, field_validator


class Foo(BaseModel):
    count: int
    size: float | None = None


class Bar(BaseModel):
    apple: str = 'x'
    banana: str = 'y'


class Spam(BaseModel):
    foo: Foo
    bars: list[Bar]

cart = Spam(
    foo={'count': 4},
    bars=[
        {'apple': 'x1'},
        {'apple': 'x2'},
    ],
)

print(cart)


class CheckInfo(BaseModel):
    check_id: str
    amount: float
    currency: str

    @field_validator('check_id')
    def validate_check_id(cls, v):
        if '-' not in v or v.split('-')[0] not in 'CHK' or len(v.split('-')[1]) != 5:
            raise ValueError('task_key must be in format PROJ-123')
        return v

    @field_validator('amount')
    def validate_amount(cls, v):
        if v <= 0 or '.' not in str(v) or len(str(v).split('.')[1]) > 2:
            raise ValueError('task_key must be in format PROJ-123')
        return v

    @field_validator('currency')
    def validate_currency(cls, v):
        if v not in ['RUB', 'USD', 'EUR']:
            raise ValueError('Wrong currency')
        return v

ddd = CheckInfo(check_id="CHK-67890", amount=1500.50, currency="RUB")
print(ddd)