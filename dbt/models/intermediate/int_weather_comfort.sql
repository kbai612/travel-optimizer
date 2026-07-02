with monthly as (
    select
        iata,
        observed_month as month,
        avg(temp_mean_c) as avg_temp_mean_c,
        avg(precipitation_hours) as avg_precip_hours,
        avg(windspeed_max_kmh) as avg_windspeed_kmh
    from {{ ref('stg_weather') }}
    group by 1, 2
),

-- 21C mean daily temp is treated as "ideal"; each sub-score falls off from 100 as the
-- month's average drifts from that comfort baseline (colder/hotter, rainier, windier).
scored as (
    select
        iata,
        month,
        round(avg_temp_mean_c, 1) as avg_temp_mean_c,
        round(avg_precip_hours, 1) as avg_precip_hours,
        round(avg_windspeed_kmh, 1) as avg_windspeed_kmh,
        greatest(0, 100 - abs(avg_temp_mean_c - 21) * 4) as temp_score,
        greatest(0, 100 - avg_precip_hours * 3) as precip_score,
        greatest(0, 100 - greatest(0, avg_windspeed_kmh - 15) * 2) as wind_score
    from monthly
)

select
    iata,
    month,
    avg_temp_mean_c,
    avg_precip_hours,
    avg_windspeed_kmh,
    round(least(100, temp_score * 0.5 + precip_score * 0.3 + wind_score * 0.2), 1) as weather_comfort_score
from scored
