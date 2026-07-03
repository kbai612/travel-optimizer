with advisory as (
    select
        country_code,
        level,
        row_number() over (partition by country_code order by updated_at desc) as rn
    from {{ ref('stg_travel_advisory') }}
)

-- Advisory is per-country and static (not per-month), so it lives on the dimension
-- rather than as a monthly sub-score. Missing data defaults to no penalty (100) rather
-- than assuming risk that hasn't been confirmed.
select
    d.iata,
    d.icao,
    d.name,
    d.country,
    d.lat,
    d.lon,
    a.level as advisory_level,
    coalesce(
        case a.level
            when 1 then 100
            when 2 then 85
            when 3 then 60
            when 4 then 30
        end,
        100
    ) as advisory_score
from {{ ref('destinations') }} d
left join advisory a on d.country = a.country_code and a.rn = 1
