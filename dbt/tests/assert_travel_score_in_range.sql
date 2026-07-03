-- Passes when zero rows are returned: every travel_score (and its sub-scores) must be 0-100.
select *
from {{ ref('fct_travel_score') }}
where travel_score < 0
   or travel_score > 100
   or weather_comfort_score < 0 or weather_comfort_score > 100
   or demand_score < 0 or demand_score > 100
   or price_score < 0 or price_score > 100
   or holiday_pressure_score < 0 or holiday_pressure_score > 100
   or air_quality_score < 0 or air_quality_score > 100
   or sea_temp_score < 0 or sea_temp_score > 100
