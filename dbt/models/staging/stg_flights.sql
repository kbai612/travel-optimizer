select
    iata,
    cast(window_start as date) as window_start,
    cast(window_end as date) as window_end,
    date_part('year', cast(window_start as date)) as sample_year,
    date_part('month', cast(window_start as date)) as sample_month,
    arrivals,
    departures,
    arrivals + departures as total_movements
from {{ source('raw', 'flights_sampled') }}
