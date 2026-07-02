with monthly as (
    select
        iata,
        period_month as month,
        avg(price) as avg_price
    from {{ ref('stg_price_monthly') }}
    where price is not null
    group by 1, 2
),

indexed as (
    select
        iata,
        month,
        avg_price,
        avg(avg_price) over (partition by iata) as dest_avg_price
    from monthly
)

select
    iata,
    month,
    avg_price,
    dest_avg_price,
    -- Price score (0-100, higher = cheaper than this destination's own average month).
    round(
        greatest(0, least(100, 100 - (avg_price / nullif(dest_avg_price, 0) * 100 - 100))),
        1
    ) as price_score
from indexed
