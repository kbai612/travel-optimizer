with monthly as (
    select
        iata,
        observed_month as month,
        avg(temp_mean_c) as avg_temp_mean_c,
        avg(precipitation_hours) as avg_precip_hours,
        avg(windspeed_max_kmh) as avg_windspeed_kmh,
        avg(apparent_temp_mean_c) as avg_apparent_temp_c,
        avg(sunshine_hours) as avg_sunshine_hours
    from {{ ref('stg_weather') }}
    group by 1, 2
),

-- 22C mean daily *feels-like* temp is treated as "ideal" -- apparent temperature already
-- folds in humidity and wind, so it's a better comfort proxy than raw air temp (a humid
-- 35C day and a dry 35C day no longer score the same). Each sub-score falls off from 100
-- as the month's average drifts from its own baseline (colder/hotter, rainier, windier,
-- less sunshine).
scored as (
    select
        iata,
        month,
        round(avg_temp_mean_c, 1) as avg_temp_mean_c,
        round(avg_precip_hours, 1) as avg_precip_hours,
        round(avg_windspeed_kmh, 1) as avg_windspeed_kmh,
        round(avg_apparent_temp_c, 1) as avg_apparent_temp_c,
        round(avg_sunshine_hours, 1) as avg_sunshine_hours,
        greatest(0, 100 - abs(avg_apparent_temp_c - 22) * 4) as feels_score,
        greatest(0, 100 - avg_precip_hours * 3) as precip_score,
        greatest(0, 100 - greatest(0, avg_windspeed_kmh - 15) * 2) as wind_score,
        least(100, avg_sunshine_hours * 12.5) as sunshine_score
    from monthly
)

select
    iata,
    month,
    avg_temp_mean_c,
    avg_precip_hours,
    avg_windspeed_kmh,
    avg_apparent_temp_c,
    avg_sunshine_hours,
    round(
        least(100, feels_score * 0.45 + precip_score * 0.25 + sunshine_score * 0.20 + wind_score * 0.10),
        1
    ) as weather_comfort_score
from scored
