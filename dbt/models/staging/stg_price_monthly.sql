select
    iata,
    origin,
    period,
    cast(split_part(period, '-', 1) as integer) as period_year,
    cast(split_part(period, '-', 2) as integer) as period_month,
    price,
    collected_at
from {{ source('raw', 'price_monthly') }}
