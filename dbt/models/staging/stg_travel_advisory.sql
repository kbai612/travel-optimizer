select
    country_code,
    level,
    cast(updated as timestamp) as updated_at
from {{ source('raw', 'travel_advisory') }}
