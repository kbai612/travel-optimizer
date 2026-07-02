with by_month as (
    select
        iata,
        holiday_month as month,
        count(*) as holiday_count,
        count(distinct holiday_year) as year_count
    from {{ ref('stg_holidays') }}
    group by 1, 2
)

select
    iata,
    month,
    round(holiday_count::double / nullif(year_count, 0), 2) as avg_holidays_per_year,
    -- More recurring public holidays in a month -> more travel/price pressure -> lower score.
    -- Months with zero holidays don't get a row here; fct_travel_score treats a missing
    -- month as "no pressure" (defaults to 100) rather than joining a synthetic zero row.
    greatest(0, 100 - least(100, round(holiday_count::double / nullif(year_count, 0), 2) * 25)) as holiday_pressure_score
from by_month
