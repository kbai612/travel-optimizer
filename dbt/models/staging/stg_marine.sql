select
    iata,
    cast(observed_at as timestamp) as observed_at,
    date_part('year', cast(observed_at as timestamp)) as observed_year,
    date_part('month', cast(observed_at as timestamp)) as observed_month,
    sst_c
from {{ source('raw', 'sea_temperature') }}
