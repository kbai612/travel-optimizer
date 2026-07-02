select
    iata,
    icao,
    name,
    country,
    lat,
    lon
from {{ ref('destinations') }}
