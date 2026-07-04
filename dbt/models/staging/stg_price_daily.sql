select
    iata,
    origin,
    cast(depart_date as date) as depart_date,
    date_part('year', cast(depart_date as date)) as period_year,
    date_part('month', cast(depart_date as date)) as period_month,
    price,
    collected_at
from {{ source('raw', 'price_daily') }}
