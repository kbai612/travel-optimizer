with monthly as (
    select
        iata,
        observed_month as month,
        avg(sst_c) as avg_sst_c
    from {{ ref('stg_marine') }}
    where sst_c is not null
    group by 1, 2
)

-- Swim comfort: ~26C is treated as ideal. Cold water deters swimming faster than warm
-- water does, so the penalty below the ideal is steeper than the penalty above it.
select
    iata,
    month,
    round(avg_sst_c, 1) as avg_sst_c,
    round(
        case
            when avg_sst_c >= 26 then greatest(0, 100 - (avg_sst_c - 26) * 3)
            else greatest(0, 100 - (26 - avg_sst_c) * 5)
        end,
        1
    ) as sea_temp_score
from monthly
