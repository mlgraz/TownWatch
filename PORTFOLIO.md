# TownWatch - Portfolio Project

## Overview

This is a production-ready React Native mobile application I built to demonstrate full-stack development capabilities. The app aggregates government meeting notes and policy documents from 15+ Maryland state and local sources.

## Technical Highlights

### Frontend (React Native)
- **Cross-platform**: iOS, Android, Web using Expo
- **Modern UI**: React Native Paper (Material Design 3)
- **Navigation**: Complex navigation with drawer + tabs + modals
- **State Management**: React Context API with optimized re-renders
- **Theming**: Full dark mode implementation with persistent preferences
- **Performance**: Lazy loading, memoization, optimized list rendering

### Backend (Serverless Architecture)
- **Database**: PostgreSQL via Supabase (cloud-native)
- **Scraping**: AWS Lambda functions (Python 3.11)
- **Automation**: EventBridge scheduled daily scraping
- **Cost-efficient**: $0-25/month for production scale
- **Scalable**: Designed to handle 50 states + international

### Architecture Decisions
- **Environment-based storage**: Auto-switches between local (dev) and cloud (prod)
- **Dual storage backends**: AsyncStorage fallback for offline capability
- **Modular services**: Clean separation of concerns
- **Type-safe models**: Document entity with validation
- **Comprehensive documentation**: 700+ line README covering all aspects

### Development Practices
- **Git workflow**: Feature branches, meaningful commits
- **Documentation**: Extensive inline comments and external docs
- **Error handling**: Graceful degradation and user feedback
- **Testing approach**: Manual testing with sample data, ready for unit tests
- **Code organization**: Clear folder structure with separation of concerns

## Technical Challenges Solved

1. **Multi-source web scraping**: Built flexible scrapers handling 5+ different government website formats (Legistar, custom HTML, PDF tables)

2. **Offline-first architecture**: Implemented storage adapter pattern allowing seamless switching between local and cloud storage

3. **Performance optimization**: Used pagination, lazy loading, and memoization for smooth 60fps scrolling with large datasets

4. **Dark mode implementation**: Built complete theming system with light/dark/auto modes persisting across app restarts

5. **Complex navigation**: Implemented drawer + bottom tabs + modal stack with proper state preservation

6. **Serverless deployment**: Configured Lambda function with 24MB deployment package, environment variables, and scheduled triggers

## Technologies Used

**Frontend:**
- React Native 0.81.5
- Expo ~54.0
- React Navigation 6.x
- React Native Paper 5.x
- AsyncStorage

**Backend:**
- Supabase (PostgreSQL 15)
- AWS Lambda (Python 3.11)
- BeautifulSoup4
- AWS EventBridge

**DevOps:**
- Expo EAS
- Git/GitHub
- npm package management
- Environment-based configuration

## What I'd Add Next

Given more time, I would implement:
1. **Testing**: Jest unit tests, React Native Testing Library integration tests
2. **CI/CD**: GitHub Actions for automated testing and deployment
3. **Authentication**: Supabase Auth for user accounts
4. **Push notifications**: Expo Notifications for new document alerts
5. **Analytics**: Track user engagement and popular documents
6. **Advanced schema**: Migrate to optimized partitioned schema for better performance at scale
7. **A/B testing**: Experiment framework for UI improvements

## Running the Project

See `README.md` for complete setup instructions.

**Quick start:**
```bash
npm install
npm start
# Tap "Load Sample Data" in app
```

## License Note

This code is available for portfolio review only. See `LICENSE` file for details. I'm happy to discuss the implementation in detail during interviews.

## Contact

For questions about this project or to discuss employment opportunities, please reach out via:
- Email: [your-email@example.com]
- LinkedIn: [your-linkedin-profile]
- Portfolio: [your-portfolio-website]

---

**Built by Matthew Graziani | 2025**
