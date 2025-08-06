from pgsql_parser.sql_parser import AdvancedSQLParser


def test_cte_query():
    sql = """WITH category_sales AS (
    -- Subquery to calculate the total sales per product.
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        SUM(p.price * s.quantity) AS total_sales
    FROM
        company_data.sales AS s
    JOIN
        company_data.products AS p ON s.product_id = p.product_id
    GROUP BY
        p.product_id, p.product_name, p.category
)
SELECT
    product_name,
    category,
    total_sales,

    -- Use SUM with an OVER clause to calculate a running total of sales within each category.
    SUM(total_sales) OVER (
        PARTITION BY category
        ORDER BY total_sales DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total_sales,

    -- Use RANK to assign a rank to each product based on its sales within its category.
    -- This allows us to easily filter for the top N products later.
    RANK() OVER (
        PARTITION BY category
        ORDER BY total_sales DESC
    ) AS category_rank
FROM
    category_sales
ORDER BY
    category, total_sales DESC; 
"""
    parser = AdvancedSQLParser(sql)
    print(parser.get_tables())
