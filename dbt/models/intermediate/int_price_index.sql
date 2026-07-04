-- Combine the two Travelpayouts fare sources into one monthly price signal per
-- destination. Daily calendar fares are strictly more granular, so where a destination
-- has calendar coverage for a (year, month) we use the average of its daily fares;
-- otherwise we fall back to the monthly-cheapest endpoint. Within each source, every
-- accumulated snapshot is averaged equally.

with daily_rolled as (
    select
        iata,
        period_year,
        period_month,
        avg(price) as month_price
    from {{ ref('stg_price_daily') }}
    where price is not null
    group by 1, 2, 3
),

monthly_rolled as (
    select
        iata,
        period_year,
        period_month,
        avg(price) as month_price
    from {{ ref('stg_price_monthly') }}
    where price is not null
    group by 1, 2, 3
),

-- One price per (iata, year, month): prefer daily, fall back to monthly where the
-- calendar endpoint has no coverage for that destination-month.
combined as (
    select iata, period_year, period_month, month_price from daily_rolled
    union all
    select m.iata, m.period_year, m.period_month, m.month_price
    from monthly_rolled m
    left join daily_rolled d
        on m.iata = d.iata
        and m.period_year = d.period_year
        and m.period_month = d.period_month
    where d.iata is null
),

monthly as (
    select
        iata,
        period_month as month,
        avg(month_price) as avg_price
    from combined
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
