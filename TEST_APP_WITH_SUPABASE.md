# Test Mobile App with Real Supabase Data

## ✅ What's Ready

1. ✅ **Supabase Database**: 10 documents with real PDF-extracted content
2. ✅ **PDF Extraction**: Working (2,000+ chars per document)
3. ✅ **Environment**: `.env.test` configured with Supabase credentials (ignored by git)
4. ✅ **Mobile App**: Ready to connect to Supabase

## 🚀 How to Test

### Start the App in Test Mode

```bash
cp .env.example .env.test   # if you haven't created it yet
# Edit .env.test with your Supabase credentials
```

```bash
# In the project root directory
NODE_ENV=test npm start -- --clear
```

Or use the Expo start script:

```bash
NODE_ENV=test npx expo start --clear
```

Then select:
- Press **`i`** for iOS Simulator
- Press **`a`** for Android Emulator
- Or scan QR code with Expo Go app on your phone

### What to Test

The app will now load **10 real Baltimore Board of Estimates documents** from Supabase:

1. **Home Screen**
   - Should load 10 documents automatically
   - Each document shows real content (not "check website for details")
   - Content is 2,000+ characters of actual meeting agendas

2. **Search Functionality**
   - Search for: "Fire Department" → should find results
   - Search for: "Real Property" → should find results
   - Search for: "Grant Award" → should find results
   - Search for: "Employee Travel" → should find results

3. **Document Detail**
   - Tap any document
   - Should see full agenda with:
     - Table of contents
     - Agenda item numbers (SB-25-xxxxx)
     - Department names
     - Contract descriptions
     - Real meeting content!

4. **Filter by Date**
   - Tap filter button
   - Filter by date range (June - November 2025)
   - Should see documents from that range

## 📊 Expected Results

### Document Content Quality

**Before (old generic content):**
```
"Board of Estimates meeting held on November 5, 2025.
Agenda and President's Memorandum available for review."
```

**After (real PDF extraction):**
```
"Board of Estimates
Council President Zeke Cohen Office of the Comptroller
Mayor Brandon M. Scott 100 Holliday Street Room 204
...
TABLE OF CONTENTS
P 2 SB-25-13834 - No Agency - Proposals & Specifications
P 3 SB-25-13937 - Real Property - Leasing
P 4 SB-25-13758 - Audit - Biennial Performance Audit
P 5-6 SB-25-13954 - Personnel - Employee Travel Request
..."
```

### Search Works on Real Content

Users can now search for:
- Specific agenda items: "SB-25-13834"
- Departments: "Fire", "Finance", "DPW"
- Topics: "Audit", "Real Property", "Grant Award"
- Actions: "Employee Travel", "Contract of Sale"

This was **impossible** with the old generic content!

## 🎯 Success Criteria

✅ **All 10 documents load** from Supabase
✅ **Content is searchable** (2,000+ chars each)
✅ **Search finds relevant results** based on real agenda content
✅ **Document detail shows** full meeting agendas
✅ **No "check website for details"** messages

## 🐛 Troubleshooting

### "No documents found"

1. Check that `.env.test` exists (create it from `.env.example`) and has correct Supabase credentials
2. Verify `NODE_ENV=test` is set
3. Check Metro bundler logs for errors
4. Restart with: `NODE_ENV=test npm start -- --clear`

### "Network request failed"

1. Check your internet connection
2. Verify Supabase URL is accessible: https://your-project-id.supabase.co
3. Check if Supabase project is active (not paused)

### "Documents load but content is generic"

This means the update didn't work. Check:
1. Run `lambda-scraper/inspect_schema.py` to verify content in database
2. If content is still generic, re-run: `lambda-scraper/update_documents_with_pdf_content.py`

## 🎉 What This Proves

By testing the mobile app now, you're verifying the **full production workflow**:

```
Scraper → PDF Extraction → Summarization → Supabase → Mobile App
```

This is exactly what will happen in production when:
1. Lambda scraper runs daily
2. Extracts PDFs from government websites
3. Stores in Supabase
4. Users open the app and see real, searchable content

---

**Ready to test?** Run `NODE_ENV=test npm start -- --clear` and see your real government data! 🚀
