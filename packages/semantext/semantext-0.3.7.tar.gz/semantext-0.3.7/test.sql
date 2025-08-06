WITH "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee" AS (
  SELECT DISTINCT
    "datalake"."remix"."dim_snif"."snif_id" AS "snif_id",
    "datalake"."remix"."dim_snif"."snif_name" AS "snif_name",
    "datalake"."remix"."dim_snif"."ir" AS "ir"
  FROM "datalake"."remix"."dim_snif"
  WHERE
    "datalake"."remix"."dim_snif"."ir" = CAST('Jerusalem' AS VARCHAR)
), "0f82c6c1-87b7-4003-a54c-faa918749d4f" AS (
  SELECT
    AVG("datalake"."remix"."sales_fact"."amount") AS "sales_fact_amount",
    SUM("datalake"."remix"."sales_fact"."price") AS "sales_fact_price",
    "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"."snif_id" AS "snif_id"
  FROM "datalake"."remix"."sales_fact"
  INNER JOIN "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"
    ON "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"."snif_id" = "datalake"."remix"."sales_fact"."snif_id"
  WHERE
    "datalake"."remix"."sales_fact"."taarich" = CAST('2023-01-01' AS TIMESTAMP)
  GROUP BY
    "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"."snif_id"
), "8a2239bc-0463-4c01-99c2-d26602ebbb5f" AS (
  SELECT
    AVG("datalake"."remix"."shalom_fact"."amount") AS "shalom_fact_amount",
    "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"."ir" AS "ir"
  FROM "datalake"."remix"."shalom_fact"
  INNER JOIN "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"
    ON "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"."ir" = "datalake"."remix"."shalom_fact"."ir"
  GROUP BY
    "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"."ir"
)
SELECT
  "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"."snif_id" AS "snif_id",
  "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"."snif_name" AS "snif_name",
  "0f82c6c1-87b7-4003-a54c-faa918749d4f"."sales_fact_amount",
  "0f82c6c1-87b7-4003-a54c-faa918749d4f"."sales_fact_price",
  "8a2239bc-0463-4c01-99c2-d26602ebbb5f"."shalom_fact_amount"
FROM "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"
LEFT JOIN "0f82c6c1-87b7-4003-a54c-faa918749d4f"
  ON "0f82c6c1-87b7-4003-a54c-faa918749d4f"."snif_id" = "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"."snif_id"
LEFT JOIN "8a2239bc-0463-4c01-99c2-d26602ebbb5f"
  ON "8a2239bc-0463-4c01-99c2-d26602ebbb5f"."ir" = "3bc9eafb-8c83-41f6-b286-b8cc3710d6ee"."ir"