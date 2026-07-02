with flights_monthly as (
    select iata, sample_month as month, avg(total_movements) as avg_movements
    from {{ ref('stg_flights') }}
    group by 1, 2
),

-- Relative index: 100 = this destination's own average month, so it stays comparable
-- across airports of very different sizes (JFK vs. KEF). OpenSky flight volume is the
-- sole demand signal (Amadeus's busiest-period API, which used to complement it, was
-- discontinued when Amadeus decommissioned its self-service portal on 2026-07-17).
flights_indexed as (
    select
        iata,
        month,
        avg_movements,
        round(avg_movements / nullif(avg(avg_movements) over (partition by iata), 0) * 100, 1)
            as flight_relative_index
    from flights_monthly
)

select
    iata,
    month,
    flight_relative_index,
    -- Busyness index (0-100, higher = busier than average), rescaled from the
    -- ~0-200 relative index. Missing data defaults to neutral (50).
    round(coalesce(least(200, greatest(0, flight_relative_index)), 100) / 2, 1) as busyness_index,
    round(100 - coalesce(least(200, greatest(0, flight_relative_index)), 100) / 2, 1) as demand_score
from flights_indexed
