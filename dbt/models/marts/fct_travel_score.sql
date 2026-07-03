{% set w_weather = var('weight_weather') %}
{% set w_demand = var('weight_demand') %}
{% set w_price = var('weight_price') %}
{% set w_holiday = var('weight_holiday') %}
{% set w_air_quality = var('weight_air_quality') %}
{% set w_sea_temp = var('weight_sea_temp') %}

-- One row per (destination, calendar month), regardless of which optional signals
-- (flights, demand, price, air quality, sea temperature) have data yet — see
-- warehouse/load.py for why those raw tables always exist even when empty. Missing
-- sub-scores default to neutral so the travel_score is always computable from whatever
-- signals are currently populated.
with spine as (
    select d.iata, d.name, d.country, d.advisory_level, d.advisory_score, m.month
    from {{ ref('dim_destination') }} d
    cross join generate_series(1, 12) as m(month)
),

-- Destinations with any real Nager.Date coverage at all. A destination with zero rows
-- here (e.g. Bangkok — Thailand isn't covered by Nager.Date) gets every month's
-- holiday_pressure_score defaulted to 100, which is indistinguishable from a covered
-- destination's genuinely-zero-holidays month unless tracked separately here.
holiday_coverage as (
    select distinct iata from {{ ref('int_holiday_pressure') }}
),

blended as (
    select
        s.iata,
        s.name,
        s.country,
        s.month,
        s.advisory_level,
        s.advisory_score,
        coalesce(w.weather_comfort_score, 50) as weather_comfort_score,
        coalesce(dm.demand_score, 50) as demand_score,
        coalesce(p.price_score, 50) as price_score,
        -- Unindexed cheapest fare (USD), left null rather than defaulted — there's no
        -- sensible neutral dollar figure the way there is for a 0-100 score.
        p.avg_price as avg_price,
        coalesce(h.holiday_pressure_score, 100) as holiday_pressure_score,
        coalesce(aq.air_quality_score, 50) as air_quality_score,
        coalesce(st.sea_temp_score, 50) as sea_temp_score,
        w.weather_comfort_score is not null as has_weather,
        dm.demand_score is not null as has_demand,
        p.price_score is not null as has_price,
        hc.iata is not null as has_holiday,
        aq.air_quality_score is not null as has_air_quality,
        st.sea_temp_score is not null as has_sea_temp,
        -- Weight-weighted share of the score backed by real data (0-1), not just a count of
        -- populated signals — a destination missing its heaviest-weighted signal is less
        -- trustworthy than one missing its lightest.
        round(
            (case when w.weather_comfort_score is not null then {{ w_weather }} else 0 end)
            + (case when dm.demand_score is not null then {{ w_demand }} else 0 end)
            + (case when p.price_score is not null then {{ w_price }} else 0 end)
            + (case when hc.iata is not null then {{ w_holiday }} else 0 end)
            + (case when aq.air_quality_score is not null then {{ w_air_quality }} else 0 end)
            + (case when st.sea_temp_score is not null then {{ w_sea_temp }} else 0 end),
            2
        ) as data_confidence,
        round(
            coalesce(w.weather_comfort_score, 50) * {{ w_weather }}
            + coalesce(dm.demand_score, 50) * {{ w_demand }}
            + coalesce(p.price_score, 50) * {{ w_price }}
            + coalesce(h.holiday_pressure_score, 100) * {{ w_holiday }}
            + coalesce(aq.air_quality_score, 50) * {{ w_air_quality }}
            + coalesce(st.sea_temp_score, 50) * {{ w_sea_temp }},
            1
        ) as blended_score
    from spine s
    left join {{ ref('int_weather_comfort') }} w on s.iata = w.iata and s.month = w.month
    left join {{ ref('int_demand_index') }} dm on s.iata = dm.iata and s.month = dm.month
    left join {{ ref('int_price_index') }} p on s.iata = p.iata and s.month = p.month
    left join {{ ref('int_holiday_pressure') }} h on s.iata = h.iata and s.month = h.month
    left join {{ ref('int_air_quality') }} aq on s.iata = aq.iata and s.month = aq.month
    left join {{ ref('int_sea_temperature') }} st on s.iata = st.iata and s.month = st.month
    left join holiday_coverage hc on s.iata = hc.iata
)

-- Safety advisory is per-country and static (not seasonal), so it's applied as a
-- multiplier on the blended monthly score rather than as one more additive weight --
-- a Level 4 country should visibly tank every month's score, which a small additive
-- term wouldn't do.
select
    iata,
    name,
    country,
    month,
    advisory_level,
    weather_comfort_score,
    demand_score,
    price_score,
    avg_price,
    holiday_pressure_score,
    air_quality_score,
    sea_temp_score,
    has_weather,
    has_demand,
    has_price,
    has_holiday,
    has_air_quality,
    has_sea_temp,
    data_confidence,
    round(blended_score * advisory_score / 100.0, 1) as travel_score
from blended
order by iata, month
