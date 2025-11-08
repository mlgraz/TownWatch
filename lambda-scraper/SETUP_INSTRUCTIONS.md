# Full Production Workflow Setup

Follow these steps to replicate the production workflow locally.

## 🎯 Overview

1. Create Supabase project (5 min)
2. Run SQL schema (2 min)
3. Get API credentials (1 min)
4. Configure environment (1 min)
5. Run scraper → stores in Supabase (2 min)
6. Test mobile app with real data (5 min)

**Total time: ~15 minutes**

---

## Step 1: Create Supabase Project

1. Go to **https://supabase.com**
2. Click **"Start your project"** and sign up/login
3. Click **"New Project"**
4. Fill in:
   - **Name**: `TownWatch` (or any name you like)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you (e.g., US East)
   - **Plan**: Free tier (perfect for testing)
5. Click **"Create new project"**
6. Wait ~2 minutes for project to be ready

---

## Step 2: Create Database Schema

1. In your Supabase dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"New Query"**
3. Copy the contents of `setup_supabase.sql` and paste into the editor

   **OR** just copy this:
   ```sql
   -- See setup_supabase.sql for the full schema
   ```

4. Click **"Run"** (or press Cmd/Ctrl + Enter)
5. You should see: `"Documents table created successfully"`

---

## Step 3: Get Your API Credentials

1. In Supabase dashboard, go to **Settings** → **API** (left sidebar)
2. Find these two values:

   **Project URL:**
   ```
   https://xxxxxxxxxxxxx.supabase.co
   ```

   **anon public key:** (starts with "eyJ...")
   ```
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

3. **Copy both values** - you'll need them in the next step

---

## Step 4: Configure Environment Variables

### For the Lambda Scraper:

Create a file: `lambda-scraper/.env`

```bash
# Copy this template and fill in your values:
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Replace** `xxxxxxxxxxxxx` and `eyJhbG...` with your actual values from Step 3.

### For the Mobile App:

Create (or edit) `.env.test` in the project root. The file is git-ignored, so it's safe to store local credentials there:

```bash
cp .env.example .env.test
NODE_ENV=test

# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Again, use your actual values from Step 3.

---

## Step 5: Run Scraper to Store in Supabase

Now run the scraper with Supabase configured:

```bash
cd lambda-scraper

# Make sure virtual environment is activated
source test_env/bin/activate

# Run the scraper (will store in Supabase this time!)
python maryland_scraper.py
```

You should see:
```
✅ Scraping complete!
   Stored: 10
   Duplicates: 0
   Errors: 0
```

---

## Step 6: Verify Data in Supabase

1. Go back to Supabase dashboard
2. Click **"Table Editor"** (left sidebar)
3. Click on **"documents"** table
4. You should see 10 rows of Baltimore Board of Estimates documents!
5. Click on a row to see the full content

---

## Step 7: Test Mobile App with Real Data

```bash
cd ..  # Back to project root

# Install dependencies if needed
npm install

# Start with test environment (uses Supabase)
NODE_ENV=test npm start -- --clear
```

When the app loads:
- It will connect to Supabase
- Load the 10 real documents you just scraped
- You can search, filter, and browse real government data!

---

## 🎉 Success!

You've just replicated the full production workflow:

✅ Scraped real government websites
✅ Extracted PDF content (10 agendas)
✅ Created summaries (2,000+ chars each)
✅ Stored in Supabase cloud database
✅ Mobile app accessing real data

---

## Troubleshooting

### "Connection refused" or "Invalid API key"

- Double-check your `SUPABASE_URL` and `SUPABASE_KEY` in `.env` files
- Make sure there are no extra spaces or quotes
- Verify the project URL starts with `https://`
- Verify the key starts with `eyJ`

### "No documents showing in app"

- Check Supabase Table Editor - are documents there?
- Make sure `.env.test` has correct credentials
- Make sure you started app with `NODE_ENV=test`
- Check browser console / Metro logs for errors

### "Permission denied" in Supabase

- Make sure you ran the SQL schema (Step 2)
- Check that RLS policies were created (see setup_supabase.sql)
- In Supabase, go to Authentication → Policies and verify public access is enabled

---

## Next Steps

Once this works, you can:

1. **Deploy scraper to AWS Lambda**
   - Set up Lambda function
   - Add same environment variables
   - Schedule to run daily
   - Documents auto-sync to app!

2. **Deploy mobile app**
   - Run `expo build`
   - Submit to App Store / Google Play
   - Users get real government data!

3. **Add more sources**
   - Edit `maryland_scraper.py`
   - Add more cities/counties
   - Re-deploy Lambda
   - More data flows automatically!

---

**Questions?** Check the logs or review:
- `SUPABASE_SETUP.md` for detailed setup
- `lambda-scraper/README_TEXT_EXTRACTION.md` for scraper details
