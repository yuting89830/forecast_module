-- SELECT * FROM devices;

SELECT
  -- TID AS "time",
  -- MAC AS metric,
  -- count(SN) AS "SN"
  *
FROM devices
WHERE
  TID >= 1690424852 AND TID <= 1690468052
GROUP BY MAC,2
ORDER BY TID;