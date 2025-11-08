import React, { createContext, useContext, useState, useEffect } from 'react';
import StorageAdapter from '../services/StorageAdapter';
import SearchService from '../services/SearchService';
import { FilterOptions } from '../models';

const DocumentContext = createContext();

export const useDocuments = () => {
  const context = useContext(DocumentContext);
  if (!context) {
    throw new Error('useDocuments must be used within a DocumentProvider');
  }
  return context;
};

export const DocumentProvider = ({ children }) => {
  const [documents, setDocuments] = useState([]);
  const [filteredDocuments, setFilteredDocuments] = useState([]);
  const [filterOptions, setFilterOptions] = useState(new FilterOptions());
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  // Apply filters whenever documents or filter options change
  useEffect(() => {
    applyFilters();
  }, [documents, filterOptions, sortBy, sortOrder]);

  const loadDocuments = async () => {
    setLoading(true);
    const docs = await StorageAdapter.getAllDocuments();
    setDocuments(docs);
    setLoading(false);
  };

  const applyFilters = () => {
    let results = SearchService.searchDocuments(documents, filterOptions);
    results = SearchService.sortDocuments(results, sortBy, sortOrder);
    setFilteredDocuments(results);
  };

  const addDocument = async (documentData) => {
    const newDoc = await StorageAdapter.addDocument(documentData);
    if (newDoc) {
      setDocuments(prev => [...prev, newDoc]);
      return newDoc;
    }
    return null;
  };

  const updateDocument = async (id, updates) => {
    const updated = await StorageAdapter.updateDocument(id, updates);
    if (updated) {
      setDocuments(prev =>
        prev.map(doc => (doc.id === id ? updated : doc))
      );
      return updated;
    }
    return null;
  };

  const deleteDocument = async (id) => {
    const success = await StorageAdapter.deleteDocument(id);
    if (success) {
      setDocuments(prev => prev.filter(doc => doc.id !== id));
    }
    return success;
  };

  const toggleFavorite = async (id) => {
    const updated = await StorageAdapter.toggleFavorite(id);
    if (updated) {
      setDocuments(prev =>
        prev.map(doc => (doc.id === id ? updated : doc))
      );
    }
  };

  const updateFilters = (newFilters) => {
    setFilterOptions(new FilterOptions(newFilters));
  };

  const resetFilters = () => {
    setFilterOptions(new FilterOptions());
  };

  const updateSort = (newSortBy, newSortOrder) => {
    setSortBy(newSortBy);
    setSortOrder(newSortOrder);
  };

  const getAllTopics = () => SearchService.getAllTopics(documents);
  const getAllJurisdictions = () => SearchService.getAllJurisdictions(documents);
  const getAllSources = () => SearchService.getAllSources(documents);

  const value = {
    documents,
    filteredDocuments,
    filterOptions,
    loading,
    sortBy,
    sortOrder,
    addDocument,
    updateDocument,
    deleteDocument,
    toggleFavorite,
    updateFilters,
    resetFilters,
    updateSort,
    getAllTopics,
    getAllJurisdictions,
    getAllSources,
    refreshDocuments: loadDocuments,
  };

  return (
    <DocumentContext.Provider value={value}>
      {children}
    </DocumentContext.Provider>
  );
};
