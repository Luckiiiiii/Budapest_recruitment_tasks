DROP TABLE IF EXISTS Products;

-- Create the table
CREATE TABLE Products
(
    id               INT PRIMARY KEY,
    PRODUCT          CHAR(1),
    SHARE            FLOAT,
    GROUP_CAPACITY   FLOAT,
    CAPACITY         FLOAT,
    INDIVIDUAL_LIMIT FLOAT,
    OVERLIMIT        TINYINT,
    ALLOCAT          FLOAT,
    NEW_ALLOC_SHARE  FLOAT,
    NEW_OVERLIMIT    TINYINT
);

-- Insert the data
INSERT INTO Products (id, PRODUCT, SHARE, GROUP_CAPACITY, CAPACITY, INDIVIDUAL_LIMIT, OVERLIMIT, ALLOCAT,
                      NEW_ALLOC_SHARE, NEW_OVERLIMIT)
VALUES (0, 'A', 0.30, 1000.0, 300.0, 200.0, 1, NULL, NULL, NULL),
       (1, 'B', 0.10, 1000.0, 100.0, 110.0, 0, NULL, NULL, NULL),
       (2, 'C', 0.05, 1000.0, 50.0, NULL, 0, NULL, NULL, NULL),
       (3, 'D', 0.49, 1000.0, 490.0, 500.0, 0, NULL, NULL, NULL),
       (4, 'E', 0.06, 1000.0, 60.0, NULL, 0, NULL, NULL, NULL);

WITH InitialData AS (
    SELECT
        id,
        PRODUCT,
        SHARE,
        GROUP_CAPACITY,
        CAPACITY,
        COALESCE(INDIVIDUAL_LIMIT, 1e10) AS INDIVIDUAL_LIMIT,
        OVERLIMIT,
        SUM(CAPACITY) OVER () AS TotalDemand
    FROM Products
),
InitialAllocation AS (
    SELECT
        id,
        PRODUCT,
        GROUP_CAPACITY,
        CAPACITY,
        INDIVIDUAL_LIMIT,
        OVERLIMIT,
        TotalDemand,
        LEAST(CAPACITY / TotalDemand * GROUP_CAPACITY, INDIVIDUAL_LIMIT) AS ALLOCAT
    FROM InitialData
),
SurplusCalculation AS (
    SELECT
        GROUP_CAPACITY - SUM(ALLOCAT) AS Surplus
    FROM InitialAllocation
),
RedistributionEligible AS (
    SELECT
        id,
        PRODUCT,
        CAPACITY,
        INDIVIDUAL_LIMIT,
        ALLOCAT,
        INDIVIDUAL_LIMIT - ALLOCAT AS RemainingRoom,
        TotalDemand
    FROM InitialAllocation
    WHERE INDIVIDUAL_LIMIT > ALLOCAT -- Only products that can receive more allocation
),
RedistributedAllocation AS (
    SELECT
        r.id,
        r.PRODUCT,
        r.CAPACITY,
        r.INDIVIDUAL_LIMIT,
        r.ALLOCAT +
        CASE
            WHEN s.Surplus > 0 THEN
                LEAST(
                    (r.RemainingRoom),
                    (r.CAPACITY / NULLIF(r.TotalDemand, 0)) * s.Surplus
                )
            ELSE 0
        END AS AdjustedAllocation
    FROM RedistributionEligible r
    CROSS JOIN SurplusCalculation s
),
FinalAllocation AS (
    SELECT
        i.id,
        i.PRODUCT,
        i.CAPACITY,
        i.INDIVIDUAL_LIMIT,
        i.GROUP_CAPACITY,
        COALESCE(ra.AdjustedAllocation, i.ALLOCAT) AS FinalAlloc,
        TotalDemand
    FROM InitialAllocation i
    LEFT JOIN RedistributedAllocation ra
    ON i.id = ra.id
),
FinalResult AS (
    SELECT
        id,
        PRODUCT,
        CAPACITY,
        INDIVIDUAL_LIMIT,
        FinalAlloc AS ALLOCAT,
        FinalAlloc / GROUP_CAPACITY AS NEW_ALLOC_SHARE,
        CASE
            WHEN FinalAlloc <= INDIVIDUAL_LIMIT THEN 0
            ELSE 1
        END AS NEW_OVERLIMIT
    FROM FinalAllocation
)

SELECT *
FROM FinalResult
ORDER BY PRODUCT ASC;


# #,id,PRODUCT,CAPACITY,INDIVIDUAL_LIMIT,ALLOCAT,NEW_ALLOC_SHARE,NEW_OVERLIMIT
# 1,0,A,300,200,200,0.2,0
# 2,1,B,100,110,110,0.11,0
# 3,2,C,50,10000000000,55,0.055,0
# 4,3,D,490,500,500,0.5,0
# 5,4,E,60,10000000000,66,0.066,0
# New total capacity 931