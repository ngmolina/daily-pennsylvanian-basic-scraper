# GitHub Actions Schedule Explanation

## Current Schedule

The current cron expression in our GitHub Actions workflow is:

```yaml
cron: "0 20 * * *"
```

This expression can be broken down into five fields:

| Field | Value | Meaning |
|-------|-------|---------|
| Minute | 0 | Run at minute 0 (top of the hour) |
| Hour | 20 | Run at 20:00 (8:00 PM) UTC |
| Day of Month | * | Run every day of the month |
| Month | * | Run every month |
| Day of Week | * | Run on every day of the week |

In other words, this schedule instructs our scraper to run once per day at exactly 8:00 PM UTC time. This corresponds to 4:00 PM Eastern Time.

## Modified Schedule for Twice-Daily Runs

I've modified the schedule to run twice daily with this cron expression:

```yaml
cron: "0 8,20 * * *"
```

This runs the scraper at:
- 8:00 AM UTC (early morning US Eastern time)
- 8:00 PM UTC (afternoon US Eastern time)