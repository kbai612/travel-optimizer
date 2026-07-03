with monthly as (
    select
        iata,
        observed_month as month,
        avg(pm2_5) as avg_pm2_5
    from {{ ref('stg_air_quality') }}
    where pm2_5 is not null
    group by 1, 2
)

-- WHO guideline treats a 5 ug/m3 annual mean as "good" (100); score falls off from there,
-- reaching 0 around 90 ug/m3 -- wide enough to still discriminate a smoggy Bangkok/Tokyo
-- month from a clean one without every score collapsing to 0.
select
    iata,
    month,
    round(avg_pm2_5, 1) as avg_pm2_5,
    round(greatest(0, 100 - greatest(0, avg_pm2_5 - 5) * 1.2), 1) as air_quality_score
from monthly
