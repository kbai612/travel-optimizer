select
    iata,
    cast(date as date) as holiday_date,
    date_part('year', cast(date as date)) as holiday_year,
    date_part('month', cast(date as date)) as holiday_month,
    name,
    local_name,
    country_code,
    is_global,
    types
from {{ source('raw', 'holidays') }}
