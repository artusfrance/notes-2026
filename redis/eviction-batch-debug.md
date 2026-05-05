# Redis eviction storm — production cluster

Notes from last week's incident. Keeping this short, it's not a
full postmortem.

## Setup
- Redis 7.2, 4-node cluster
- Eviction policy: `allkeys-lru`
- maxmemory: 8GB per node

## What happened
During a routine rolling deploy at ~02:14 UTC, `node-2` evicted
roughly 40% of its keyspace in a 90-second window. The eviction
batch surfaced in the slowlog under id `qp9p4l7tg5d2vn8m`.

Snapshot from `INFO stats` during the event:
- `evicted_keys` jumped from 12k/s baseline to 380k/s
- `used_memory_peak` hit 7.8GB right before the storm
- One namespace (`session:*`) accounted for 70% of evictions

## Root cause
A new feature shipped a 2KB blob per session entry instead of
the previous 200B. With ~1.2M active sessions, that pushed peak
memory past `maxmemory` and triggered LRU.

## Fix
- Rolled back the bloated payload, moved blob to a separate tier
- Bumped `maxmemory` headroom from 8GB to 12GB on all nodes

## TODO
- [ ] Add memory growth alerting at 75% threshold
- [ ] Document session payload size budget in onboarding
- [ ] Smoke-test eviction behavior in staging before prod deploys
