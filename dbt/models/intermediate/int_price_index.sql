with origin_history as (
    select iata, origin, collected_at from {{ ref('stg_price_daily') }}
    union all
    select iata, origin, collected_at from {{ ref('stg_price_monthly') }}
),

latest_origin as (
    select
        iata,
        origin
    from (
        select
            iata,
            origin,
            row_number() over (
                partition by iata
                order by collected_at desc, origin desc
            ) as row_num
        from origin_history
        where origin is not null
            and collected_at is not null
    )
    where row_num = 1
),

daily_snapshot_monthly as (
    select
        d.iata,
        d.period_year,
        d.period_month,
        d.collected_at,
        avg(d.price) as month_price
    from {{ ref('stg_price_daily') }} d
    inner join latest_origin o
        on d.iata = o.iata
        and d.origin = o.origin
    where d.price is not null
    group by 1, 2, 3, 4
),

daily_rolled as (
    select
        iata,
        period_year,
        period_month,
        avg(month_price) as month_price
    from daily_snapshot_monthly
    group by 1, 2, 3
),

monthly_snapshot_monthly as (
    select
        m.iata,
        m.period_year,
        m.period_month,
        m.collected_at,
        avg(m.price) as month_price
    from {{ ref('stg_price_monthly') }} m
    inner join latest_origin o
        on m.iata = o.iata
        and m.origin = o.origin
    where m.price is not null
    group by 1, 2, 3, 4
),

monthly_rolled as (
    select
        iata,
        period_year,
        period_month,
        avg(month_price) as month_price
    from monthly_snapshot_monthly
    group by 1, 2, 3
),

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
    round(
        greatest(0, least(100, 100 - (avg_price / nullif(dest_avg_price, 0) * 100 - 100))),
        1
    ) as price_score
from indexed
