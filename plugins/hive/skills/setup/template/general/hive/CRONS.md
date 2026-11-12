# Lead crons

This table is the source of truth for the lead's scheduled jobs, because session jobs die with the session and expire after 7 days. A new lead creates any missing job with its prompt word for word, and writes the job id and expiry in its row each time it creates or renews one. Times are local. Prompts stay one line and point at repo files.

| id | cron | prompt |
|---|---|---|
| check-in | `17 * * * *` | `HIVE CHECK-IN (lead): follow hive/LEAD.md "Check-in" exactly.` |
| strategist | `47 16 * * 2` | `HIVE STRATEGIST (lead): run the idea round in hive/STRATEGIST.md, then file a bead "Strategist <UTC date>" -l role:strategist -d "Follow your brief." and spawn one unnamed one-shot agent on it with subagent_type "strategist"; post its "Report to {{owner}}" unchanged.` |
| gardener | `17 17 * * 2` | `HIVE GARDENER (lead): file a bead "Gardener <UTC date>" -l role:gardener -d "Follow your brief." and spawn one unnamed one-shot agent on it with subagent_type "gardener"; post its "Report to {{owner}}" unchanged.` |
