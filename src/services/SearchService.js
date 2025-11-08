/**
 * Service for searching and filtering documents
 */
class SearchService {
  /**
   * Search documents based on filter options
   */
  searchDocuments(documents, filterOptions) {
    let results = [...documents];

    // Text search
    if (filterOptions.searchQuery && filterOptions.searchQuery.trim() !== '') {
      const query = filterOptions.searchQuery.toLowerCase();
      results = results.filter(doc =>
        doc.title.toLowerCase().includes(query) ||
        doc.content.toLowerCase().includes(query) ||
        doc.source.toLowerCase().includes(query) ||
        doc.jurisdiction.toLowerCase().includes(query)
      );
    }

    // Filter by topics
    if (filterOptions.selectedTopics.length > 0) {
      results = results.filter(doc =>
        filterOptions.selectedTopics.some(topic => doc.topics.includes(topic))
      );
    }

    // Filter by date range
    if (filterOptions.startDate) {
      results = results.filter(doc => new Date(doc.date) >= new Date(filterOptions.startDate));
    }
    if (filterOptions.endDate) {
      results = results.filter(doc => new Date(doc.date) <= new Date(filterOptions.endDate));
    }

    // Filter by jurisdictions
    if (filterOptions.jurisdictions.length > 0) {
      results = results.filter(doc =>
        filterOptions.jurisdictions.includes(doc.jurisdiction)
      );
    }

    // Filter by sources
    if (filterOptions.sources.length > 0) {
      results = results.filter(doc =>
        filterOptions.sources.includes(doc.source)
      );
    }

    // Filter by favorites
    if (filterOptions.favoritesOnly) {
      results = results.filter(doc => doc.isFavorite);
    }

    return results;
  }

  /**
   * Get all unique topics from documents
   */
  getAllTopics(documents) {
    const topicsSet = new Set();
    documents.forEach(doc => {
      doc.topics.forEach(topic => topicsSet.add(topic));
    });
    return Array.from(topicsSet).sort();
  }

  /**
   * Get all unique jurisdictions from documents
   */
  getAllJurisdictions(documents) {
    const jurisdictionsSet = new Set();
    documents.forEach(doc => {
      jurisdictionsSet.add(doc.jurisdiction);
    });
    return Array.from(jurisdictionsSet).sort();
  }

  /**
   * Get all unique sources from documents
   */
  getAllSources(documents) {
    const sourcesSet = new Set();
    documents.forEach(doc => {
      sourcesSet.add(doc.source);
    });
    return Array.from(sourcesSet).sort();
  }

  /**
   * Sort documents by various criteria
   */
  sortDocuments(documents, sortBy = 'date', order = 'desc') {
    const sorted = [...documents];

    sorted.sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case 'date':
          comparison = new Date(a.date) - new Date(b.date);
          break;
        case 'title':
          comparison = a.title.localeCompare(b.title);
          break;
        case 'jurisdiction':
          comparison = a.jurisdiction.localeCompare(b.jurisdiction);
          break;
        case 'source':
          comparison = a.source.localeCompare(b.source);
          break;
        default:
          comparison = new Date(a.date) - new Date(b.date);
      }

      return order === 'asc' ? comparison : -comparison;
    });

    return sorted;
  }
}

export default new SearchService();
