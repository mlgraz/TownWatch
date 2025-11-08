# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TownWatch is a React Native mobile application built with Expo for scanning and aggregating information from local government websites. The app stores meeting notes, policy discussions, and government documents in text form, providing users with search and filtering capabilities to easily find relevant information.

## Development Commands

### Running the Application
```bash
npm start              # Start Expo development server
npm run ios            # Run on iOS simulator
npm run android        # Run on Android emulator
npm run web            # Run in web browser
```

### Package Management
```bash
npm install            # Install dependencies
```

## Architecture

### Tech Stack
- **Framework**: React Native 0.81.5
- **React Version**: 19.1.0
- **Build Tool**: Expo ~54.0.22
- **Navigation**: React Navigation (Native Stack + Bottom Tabs)
- **UI Library**: React Native Paper
- **Storage**: Supabase (cloud PostgreSQL) + AsyncStorage fallback (local device storage)
- **Backend**: AWS Lambda (Python) for web scraping
- **State Management**: React Context API
- **Architecture**: React Native New Architecture (enabled via `newArchEnabled: true` in app.json)

### Project Structure
```
src/
├── screens/           # Screen components
│   ├── HomeScreen.js           # Main document list view (dark mode ready)
│   ├── SearchScreen.js         # Search interface (dark mode ready)
│   ├── SettingsScreen.js       # Settings with theme dropdown
│   ├── DocumentDetailScreen.js # Full document view
│   └── FilterScreen.js         # Filter configuration modal
├── components/        # Reusable components
│   ├── SampleDataButton.js     # Sample data loader
│   └── CustomDrawerContent.js  # Branded hamburger menu drawer
├── navigation/        # Navigation configuration
│   └── AppNavigator.js         # Drawer + 2-tab navigation (Home, Search) + modal stack
├── context/          # React Context providers
│   ├── DocumentContext.js      # Global document state management
│   └── ThemeContext.js         # Global theme state (light/dark/auto)
├── services/         # Business logic layer
│   ├── StorageService.js       # AsyncStorage wrapper for CRUD operations
│   ├── SupabaseStorageService.js  # Supabase cloud storage service
│   ├── StorageAdapter.js       # Environment-based storage selector
│   └── SearchService.js        # Search, filter, and sort logic
├── config/           # Configuration
│   ├── supabase.js             # Supabase client setup (lazy initialization)
│   └── environment.js          # Environment detection (dev/test/prod)
├── models/           # Data models
│   ├── Document.js             # Document entity with JSON serialization
│   └── FilterOptions.js        # Filter state model
├── theme/            # Theme configuration
│   ├── colors.js               # Light and dark color palettes
│   └── paperTheme.js           # React Native Paper theme configs
└── utils/            # Utilities
    ├── sampleData.js           # Sample government documents for testing
    └── documentIcons.js        # Document type icon/color mapping
```

### Data Model

**Document** - Represents a government meeting note or policy document
- `id`: Unique identifier (auto-generated)
- `title`: Document title
- `content`: Full text content
- `date`: Meeting/document date
- `source`: Origin (e.g., "City Council", "Planning Commission")
- `jurisdiction`: Location (e.g., "San Francisco, CA")
- `topics`: Array of topic tags for categorization
- `url`: Optional link to original source
- `isFavorite`: Boolean for user favorites
- `createdAt`: Timestamp when added to app

### State Management

The app uses React Context API for global state management:
- **DocumentContext** provides access to all documents, filtered results, and CRUD operations
- Context automatically handles filtering and sorting when data or filter options change
- All document operations (add, update, delete, toggle favorite) are async and update both state and AsyncStorage

### Data Flow

1. **Storage Layer** (`StorageService`): Handles persistence with AsyncStorage
2. **Business Logic** (`SearchService`): Implements search, filter, and sort algorithms
3. **State Management** (`DocumentContext`): Coordinates storage and services, provides data to UI
4. **UI Components**: Consume context and render document data

### Navigation Structure

- **Bottom Tab Navigator**: Home and Search tabs
- **Stack Navigator**: Overlays detail and filter screens
- Filter screen uses modal presentation
- Document detail is accessible from both Home and Search screens

### Key Features

- **Full-text search**: Search across title, content, source, and jurisdiction
- **Multi-criteria filtering**: Filter by topics, date ranges, jurisdictions, sources, and favorites
- **Sorting**: Sort documents by date, title, jurisdiction, or source
- **Favorites**: Mark important documents for quick access
- **Sample data**: Built-in sample government documents for testing

### Platform Configuration
- **Orientation**: Portrait only
- **UI Style**: Automatic (supports light/dark modes)
- **iOS**: Tablet support enabled
- **Android**: Edge-to-edge display enabled, adaptive icons configured
- **Web**: Favicon support
- **Theme**: Full dark mode support with dropdown selection in Settings

### Backend Architecture

The app uses a **serverless, cloud-based architecture** for scalability and affordability:

```
┌─────────────────┐
│  React Native   │
│  Mobile App     │
└────────┬────────┘
         │ Supabase Client
         ▼
┌─────────────────┐
│    Supabase     │
│  (PostgreSQL)   │◄─────────┐
│  - Documents    │          │
│  - Real-time    │          │
│  - Auth Ready   │          │
└─────────────────┘          │
                             │
                    ┌────────┴────────┐
                    │  AWS Lambda     │
                    │  (Python)       │
                    │                 │
                    │  - Web Scraping │
                    │  - BeautifulSoup│
                    │  - Scheduled    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Government    │
                    │    Websites     │
                    └─────────────────┘
```

**Data Flow:**
1. **AWS Lambda** runs daily (scheduled via EventBridge)
2. Lambda scrapes government websites using BeautifulSoup
3. Scraped documents are stored in **Supabase PostgreSQL**
4. **Mobile app** fetches documents directly from Supabase
5. Real-time updates push new documents to app instantly

**Storage Options:**
- **Primary**: `SupabaseStorageService` - Cloud storage with PostgreSQL (recommended)
- **Fallback**: `StorageService` - Local AsyncStorage (offline-first or no Supabase)

### Setup Instructions

**Quick Start (Local/AsyncStorage Only):**
1. `npm install`
2. `npm start`
3. Use "Load Sample Data" button in app

**Full Setup (Supabase + Lambda):**
1. Follow `SUPABASE_SETUP.md` to create database
2. Copy `.env.example` to `.env.test` (or `.env.production`) and add credentials
3. Follow `LAMBDA_SCRAPER_SETUP.md` to deploy scraper
4. Documents automatically sync to app

### Environment Variables

1. Copy the template: `cp .env.example .env.test`
2. Edit the new file and set:

```
NODE_ENV=test
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

Repeat for `.env.production` when preparing a release build. These files are ignored by git by default.

### Cost Structure

**Free Tier (0-100 users):** $0/month
- Supabase: 500MB database, 1GB storage, unlimited API requests
- AWS Lambda: 1M requests/month, 400K GB-seconds compute
- Perfect for MVP and testing

**Growth (100-1,000 users):** ~$25/month
- Supabase Pro: 8GB database, 100GB bandwidth
- Lambda still free (well under limits)

**Scale (1,000-10,000 users):** ~$50-100/month
- Additional Supabase storage/bandwidth
- Lambda charges minimal (pennies per scrape)

### Key Notes
- This is a managed Expo project - native iOS/Android folders are gitignored and regenerated
- New Architecture is enabled, which may affect how native modules are integrated
- Data can be stored locally (AsyncStorage) or in cloud (Supabase)
- Supabase provides real-time updates, full-text search, and auto-scaling
- AWS Lambda scraper runs on schedule (daily/weekly) - completely serverless
- Total infrastructure cost: $0-25/month for most use cases

## Recent Updates & Current Status

### ✅ Completed Features

#### 1. Hamburger Menu Navigation (Latest)
- **Drawer navigation** with React Navigation Drawer
- **Hamburger button** in top-left of Home screen header
- **Custom drawer content** (`src/components/CustomDrawerContent.js`): Branded drawer with app logo
- **Two-tab navigation**: Home and Search in bottom tabs
- **Settings in drawer**: Moved from bottom tab to hamburger menu
- **Theme-aware drawer**: Colors adapt to light/dark mode
- **Gesture support**: Swipe from left to open drawer
- **Dependencies added**:
  - `@react-navigation/drawer`
  - `react-native-gesture-handler`
  - `react-native-reanimated`
- **Babel configuration**: Added `babel.config.js` for reanimated plugin

**Drawer Menu Items:**
- Home (links to main tabs)
- Settings (theme selection)

#### 2. Dark Mode Implementation
- **Full theme system** with light, dark, and auto modes
- **ThemeContext** (`src/context/ThemeContext.js`): Global theme state with AsyncStorage persistence
- **Color palettes** (`src/theme/colors.js`): Complete light/dark color definitions
- **Paper themes** (`src/theme/paperTheme.js`): Material Design 3 integration
- **Settings screen** (`src/screens/SettingsScreen.js`): Dropdown menu for theme selection
- **Updated screens**: HomeScreen and SearchScreen with dynamic colors
- **StatusBar**: Automatically adapts to light/dark mode
- **Navigation**: Added Settings tab (three tabs: Home, Search, Settings)

**Theme Modes:**
- **Light**: Always light theme
- **Dark**: Always dark theme
- **Auto**: Follows device system theme

#### 2. Environment-Based Storage
- **StorageAdapter** (`src/services/StorageAdapter.js`): Auto-selects backend based on NODE_ENV
- **Development**: Uses AsyncStorage (no Supabase required)
- **Test/Production**: Uses Supabase if configured, otherwise falls back to AsyncStorage
- **Lazy Supabase initialization**: Only creates client when needed (prevents errors in dev)

#### 3. UI Enhancements
- **Document type icons** (`src/utils/documentIcons.js`): Color-coded icons for different sources
  - Legislature: Purple with gavel icon
  - Council: Blue with account-group icon
  - Board/Commission: Teal with clipboard icon
  - Planning: Green with city icon
  - Transportation: Orange with train icon
  - Budget: Red with cash icon
- **Card improvements**: Shadows, rounded corners, better spacing
- **Avatar icons**: Each document card shows colored icon badge
- **Splash screen**: Purple background (#6200ee)

#### 4. Maryland Government Scraping Infrastructure
- **15+ government sources** configured in `lambda-scraper/maryland_sources.json`
  - Maryland General Assembly
  - Baltimore City (Council, Board of Estimates, Planning Commission)
  - Multiple counties (Montgomery, Prince George's, Anne Arundel, Howard, Baltimore County)
- **Specialized scrapers** (`lambda-scraper/maryland_scraper.py`):
  - MD General Assembly meetings scraper
  - Baltimore Board of Estimates scraper
  - Legistar calendar scraper (for multiple jurisdictions)
  - PDF table parser for agendas
  - Auto-topic detection (12 categories)
  - Duplicate prevention
- **Deployment package ready**: `lambda-scraper/maryland-scraper.zip` (24MB)
- **Documentation**: `MARYLAND_SCRAPING_GUIDE.md`, `DEPLOY_MARYLAND_NOW.md`

#### 5. App Icon Design
- **Capitol dome design** created in `assets/icon-design.svg`
- Purple gradient background (#6200ee → #3700b3)
- White government building with dome and columns
- Clean, professional aesthetic
- **Conversion guide**: `ICON_CREATION_GUIDE.md` with multiple options

### 📝 Documentation Created
- `DARK_MODE_IMPLEMENTATION.md`: Complete dark mode feature documentation
- `ICON_CREATION_GUIDE.md`: Instructions for converting SVG to PNG icons
- `APP_BRANDING_GUIDE.md`: Full branding and design guidelines
- `ENVIRONMENT_SETUP.md`: Development environment configuration
- `ENVIRONMENT_SUMMARY.md`: Quick reference for environment variables
- `MARYLAND_SCRAPING_GUIDE.md`: Maryland scraper comprehensive guide
- `MARYLAND_SOURCES_SUMMARY.md`: Quick list of 15+ Maryland sources
- `DEPLOY_MARYLAND_NOW.md`: Step-by-step AWS Lambda deployment
- `SUPABASE_SETUP.md`: Database schema and setup instructions
- `LAMBDA_SCRAPER_SETUP.md`: General Lambda scraping setup

### 🔧 Fixed Issues
1. **Supabase initialization error**: Changed to lazy loading - only creates client when actually used
2. **Port conflicts**: Proper Metro Bundler cleanup procedures
3. **Environment detection**: Proper dev/test/prod environment handling

### ⏭️ Next Steps / Pending Tasks

**Icon Implementation:**
1. Convert `assets/icon-design.svg` to PNG (1024x1024)
2. Place as `assets/icon.png`
3. Create adaptive icon for Android
4. Create splash screen icon (400x400 transparent)
5. Run `npx expo prebuild --clean` to generate all sizes

**Maryland Scraper Deployment:**
1. Upload `lambda-scraper/maryland-scraper.zip` to AWS Lambda
2. Configure environment variables (SUPABASE_URL, SUPABASE_ANON_KEY)
3. Set up EventBridge trigger (daily/weekly schedule)
4. Test scraper with manual Lambda invocation

**Supabase Setup (Optional - for production):**
1. Create Supabase project
2. Run SQL schema from `SUPABASE_SETUP.md`
3. Copy `.env.example` → `.env.production` and add credentials (keep local)
4. Test cloud storage functionality

**Additional Features (Future):**
- Favorites screen/tab
- Document detail screen improvements
- Share functionality
- Export documents
- Notification system for new documents
- Advanced search with operators
- Saved searches/filters

### 🎯 Where We Left Off

**Last completed:** Implemented hamburger menu navigation with drawer. Settings moved from bottom tab to hamburger menu. The app now has:
- Two-tab bottom navigation (Home, Search)
- Hamburger menu button in top-left of Home screen
- Drawer menu with Home and Settings options
- Custom drawer content with app branding
- Full dark mode support throughout drawer
- Dropdown theme selector in Settings

**Current state:**
- App is fully functional in development mode with AsyncStorage
- Drawer navigation with hamburger menu working
- Dark mode works perfectly with dropdown theme selector
- Maryland scraper is built and packaged, ready for AWS deployment
- Icon design created, needs PNG conversion
- Supabase integration code complete, needs production setup

**Navigation Structure:**
- Bottom tabs: Home | Search
- Hamburger menu (top-left on Home): Home | Settings
- Modal screens: Document Detail, Filter

**To test current features:**
```bash
npm start -- --clear
# Then scan QR code or press 'i' for iOS, 'a' for Android
# Tap hamburger menu (☰) in top-left to open drawer
# Select Settings from drawer to try dark mode
```
