# Supabase Deployment & Setup Guide

This guide describes how to deploy the database schema, edge function, secrets, and cron scheduler to migrate your LinkedIn Intelligence Platform to a fully serverless setup on Supabase (Option B).

---

## 1. Database Setup

1. Go to your [Supabase Dashboard](https://supabase.com).
2. Select your project and navigate to the **SQL Editor**.
3. Open the file [supabase/schema.sql](file:///c:/Users/shivank/OneDrive/Desktop/agentic-wflow/postmaker/supabase/schema.sql) in this repository.
4. Copy the entire contents of the SQL script, paste it into the editor, and click **Run**.
5. This will create all required tables (`profiles`, `crawl_history`, `posts`, `scores`, `generated_comments`, and `crawl_runs`), establish foreign key indexes, and seed the initial target profiles.

---

## 2. Deploy the Edge Function

Ensure you have the Supabase CLI installed on your machine.

1. Login to the Supabase CLI (if not already logged in):
   ```bash
   supabase login
   ```
2. Initialize or link your project:
   ```bash
   supabase link --project-ref <your-project-ref>
   ```
3. Deploy the Edge Function:
   ```bash
   supabase functions deploy linkedin-agent
   ```

---

## 3. Set Up Environment Variables / Secrets

The Edge Function requires API keys to execute successfully. Set these secrets using the Supabase CLI or in the Supabase Dashboard under **Settings > Edge Functions**.

### Using the CLI:
```bash
supabase secrets set GROQ_API_KEY="your-groq-key"
supabase secrets set APIFY_API_KEY="your-apify-key"
```

*   `GROQ_API_KEY`: Required for AI scoring.
*   `APIFY_API_KEY`: Required if using Apify's pre-built LinkedIn Post Scraper actor. If you run the function without setting it, it will execute in a test/mock mode to verify DB integration.

---

## 4. Configure Automated Daily Scheduling (CRON)

To schedule the scraper agent to run every night automatically at 3:00 AM UTC (8:30 AM IST), run the following query in your Supabase **SQL Editor**:

> [!NOTE]
> Ensure the `pg_net` extension is enabled in your database settings before running this query (enabled by default on new Supabase projects).

```sql
-- Enable cron if not already enabled
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule the daily crawl at 3:00 AM UTC
SELECT cron.schedule(
  'daily-linkedin-crawl',
  '0 3 * * *',
  $$
  SELECT net.http_post(
    url := 'https://<your-project-ref>.supabase.co/functions/v1/linkedin-agent',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer <YOUR_SERVICE_ROLE_KEY>'
    ),
    body := '{}'::jsonb
  );
  $$
);
```

> [!IMPORTANT]
> Replace `<your-project-ref>` with your actual Supabase project reference and `<YOUR_SERVICE_ROLE_KEY>` with your database service role API key.

---

## 5. Configure Vercel Project Environment Variables

To allow your frontend on Vercel to query database metrics and results directly from Supabase, log into your Vercel Dashboard, go to your project settings, and add the following Environment Variables:

1.  `SUPABASE_URL`: Your Supabase API endpoint (e.g. `https://xxx.supabase.co`).
2.  `SUPABASE_ANON_KEY`: Your Supabase anonymous API key.
3.  `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role API key (needed for the scrape trigger function).

Re-deploy your Vercel site to activate the changes. The frontend will now use the new endpoints `/api/results`, `/api/metrics`, and `/api/scrape` to interact directly with Supabase!
