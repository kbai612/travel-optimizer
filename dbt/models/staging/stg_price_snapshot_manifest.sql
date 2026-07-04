select
    snapshot_source,
    iata,
    origin,
    collected_at
from {{ source('raw', 'price_snapshot_manifest') }}
