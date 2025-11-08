# Start App with Supabase Data

## 🔧 What We Just Fixed

The app wasn't loading environment variables because:
1. ❌ `react-native-dotenv` was installed but NOT configured in `babel.config.js`
2. ❌ Environment variables weren't being imported correctly

**Now fixed:**
1. ✅ `babel.config.js` now loads the correct `.env.test` file
2. ✅ `environment.js` imports from `@env`
3. ✅ Debug logging added to show what's loaded

## 🚀 How to Start the App (IMPORTANT!)

First, create a local `.env.test` (ignored by git) using the template and supply your Supabase credentials:

```bash
cp .env.example .env.test
# Edit .env.test and fill in SUPABASE_URL / SUPABASE_ANON_KEY
```

Since we changed `babel.config.js`, you MUST clear the Metro cache:

```bash
# Kill any running Metro bundlers first
killall node

# Start with cache cleared and NODE_ENV=test
NODE_ENV=test npx expo start --clear
```

**Or use the npm script:**

```bash
NODE_ENV=test npm start -- --clear
```

## 📱 What to Look For

### 1. Check the Metro Console

When the app starts, you should see:

```
🌍 Loading environment from: .env.test
🚀 App starting...
╔═══════════════════════════════════════╗
║  TownWatch Environment Configuration  ║
╚═══════════════════════════════════════╝
Environment: Testing (test)
Storage Backend: Supabase (Cloud)
Supabase URL: your-project-id.supabase.co
Supabase Key: eyJhbG…uiQo
```

**If you see `Supabase Key: Not set`**, the environment variables aren't loading.

### 2. Check the App Screen

When the app loads:
- **Should show:** 10 documents from Baltimore Board of Estimates
- **Should NOT show:** "Load Sample Data" button (that's for local mode)
- **Content should be:** Real meeting agendas (2,000+ chars), not "check website for details"

### 3. Test Search

Try searching for:
- "Fire Department" → should find results
- "Real Property" → should find results
- "Grant Award" → should find results

These searches work because we have REAL content now!

## 🐛 Troubleshooting

### "Configured: ❌ NO" in console

**Problem:** Environment variables not loading

**Solutions:**
1. Make sure you ran with `--clear` flag to clear cache
2. Kill all Metro bundlers: `killall node`
3. Restart: `NODE_ENV=test npx expo start --clear`
4. Check `.env.test` exists (create it from `.env.example`) and has correct values

### Still showing "Load Sample Data" button

**Problem:** App is using AsyncStorage (local), not Supabase

**Check:**
1. Look at Metro console - does it say "Supabase (Cloud)"?
2. If not, environment isn't loading
3. Try steps above

### "No documents found"

**Problem:** Connected to Supabase but no data

**Check:**
1. Run: `cd lambda-scraper && source test_env/bin/activate && python inspect_schema.py`
2. Should show 10 documents in database
3. If not, run: `python update_documents_with_pdf_content.py`

### TypeScript errors about '@env'

**Solution:** Create type definitions (optional):

```bash
echo "declare module '@env' {
  export const NODE_ENV: string;
  export const SUPABASE_URL: string;
  export const SUPABASE_ANON_KEY: string;
}" > src/types/env.d.ts
```

## ✅ Success Checklist

- [ ] Killed all running Metro bundlers
- [ ] Started with: `NODE_ENV=test npx expo start --clear`
- [ ] Metro console shows "Loading environment from: .env.test"
- [ ] Debug log shows "Storage Backend: Supabase (Cloud)"
- [ ] Debug log shows Supabase URL/Key (not "Not set")
- [ ] App loads 10 documents
- [ ] Content is detailed (2,000+ chars), not generic
- [ ] Search finds results for "Fire Department", "Real Property", etc.

## 🎯 Quick Test Commands

**Kill and restart cleanly:**
```bash
killall node && NODE_ENV=test npx expo start --clear
```

**Check database has data:**
```bash
cd lambda-scraper && source test_env/bin/activate && python inspect_schema.py
```

**Verify environment file:**
```bash
cat .env.test
```

---

**Once this works, you'll have proven the full production workflow!** 🎉
