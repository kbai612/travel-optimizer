{% set w_weather = var('weight_weather') %}
{% set w_demand = var('weight_demand') %}
{% set w_price = var('weight_price') %}
{% set w_holiday = var('weight_holiday') %}

-- One row per (destination, calendar month), regardless of which optional signals
-- (flights, demand, price) have data yet — see warehouse/load.py for why those raw
-- tables always exist even when empty. Missing sub-scores default to neutral so the
-- travel_score is always computable from whatever signals are currently populated.
with spine as (
    select d.iata, d.name, d.country, m.month
    from {{ ref('dim_destination') }} d
    cross join generate_series(1, 12) as m(month)
)

select
    s.iata,
    s.name,
    s.country,
    s.month,
    coalesce(w.weather_comfort_score, 50) as weather_comfort_score,
    coalesce(dm.demand_score, 50) as demand_score,
    coalesce(p.price_score, 50) as price_score,
    coalesce(h.holiday_pressure_score, 100) as holiday_pressure_score,
    round(
        coalesce(w.weather_comfort_score, 50) * {{ w_weather }}
        + coalesce(dm.demand_score, 50) * {{ w_demand }}
        + coalesce(p.price_score, 50) * {{ w_price }}
        + coalesce(h.holiday_pressure_score, 100) * {{ w_holiday }},
        1
    ) as travel_score
from spine s
left join {{ ref('int_weather_comfort') }} w on s.iata = w.iata and s.month = w.month
left join {{ ref('int_demand_index') }} dm on s.iata = dm.iata and s.month = dm.month
left join {{ ref('int_price_index') }} p on s.iata = p.iata and s.month = p.month
left join {{ ref('int_holiday_pressure') }} h on s.iata = h.iata and s.month = h.month
order by s.iata, s.month
