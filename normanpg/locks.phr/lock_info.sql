SELECT
	t.relname,
	t.schemaname,
	pid,
	mode,
	granted
FROM
	pg_locks l,
	pg_stat_all_tables t
WHERE
	l.relation=t.relid
	AND
	t.relname={table}
	AND
	t.schemaname={schema}
ORDER BY
	relation ASC;