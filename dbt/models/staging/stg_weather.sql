select
    iata,
    cast(date as date) as observed_date,
    date_part('year', cast(date as date)) as observed_year,
    date_part('month', cast(date as date)) as observed_month,
    temp_max_c,
    temp_min_c,
    temp_mean_c,
    precipitation_mm,
    precipitation_hours,
    windspeed_max_kmh
from {{ source('raw', 'weather_daily') }}
