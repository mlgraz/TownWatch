/**
 * FilterOptions model for search and filter functionality
 */

export class FilterOptions {
  constructor({
    searchQuery = '',
    selectedTopics = [],
    startDate = null,
    endDate = null,
    jurisdictions = [],
    sources = [],
    favoritesOnly = false,
  } = {}) {
    this.searchQuery = searchQuery;
    this.selectedTopics = selectedTopics;
    this.startDate = startDate;
    this.endDate = endDate;
    this.jurisdictions = jurisdictions;
    this.sources = sources;
    this.favoritesOnly = favoritesOnly;
  }

  hasActiveFilters() {
    return (
      this.searchQuery.length > 0 ||
      this.selectedTopics.length > 0 ||
      this.startDate !== null ||
      this.endDate !== null ||
      this.jurisdictions.length > 0 ||
      this.sources.length > 0 ||
      this.favoritesOnly
    );
  }

  reset() {
    this.searchQuery = '';
    this.selectedTopics = [];
    this.startDate = null;
    this.endDate = null;
    this.jurisdictions = [];
    this.sources = [];
    this.favoritesOnly = false;
  }
}
