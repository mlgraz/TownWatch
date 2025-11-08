/**
 * Storage Adapter - Automatically selects storage backend based on environment
 *
 * - Development: Uses AsyncStorage (local)
 * - Testing/Production: Uses Supabase (cloud) if configured, falls back to AsyncStorage
 */

import config, { logEnvironment } from '../config/environment';
import StorageService from './StorageService';
import SupabaseStorageService from './SupabaseStorageService';

class StorageAdapter {
  constructor() {
    // Log environment on initialization
    logEnvironment();

    // Select storage backend
    if (config.useSupabase) {
      this.backend = SupabaseStorageService;
      this.backendName = 'Supabase';
      console.log('✅ Using Supabase storage (cloud)');
    } else {
      this.backend = StorageService;
      this.backendName = 'AsyncStorage';
      console.log('✅ Using AsyncStorage (local)');
    }
  }

  /**
   * Get the name of the current storage backend
   */
  getBackendName() {
    return this.backendName;
  }

  /**
   * Check if using Supabase
   */
  isUsingSupabase() {
    return this.backendName === 'Supabase';
  }

  /**
   * Get all documents
   */
  async getAllDocuments() {
    try {
      return await this.backend.getAllDocuments();
    } catch (error) {
      console.error(`[${this.backendName}] Error getting documents:`, error);
      return [];
    }
  }

  /**
   * Add a new document
   */
  async addDocument(documentData) {
    try {
      return await this.backend.addDocument(documentData);
    } catch (error) {
      console.error(`[${this.backendName}] Error adding document:`, error);
      return null;
    }
  }

  /**
   * Update an existing document
   */
  async updateDocument(id, updates) {
    try {
      return await this.backend.updateDocument(id, updates);
    } catch (error) {
      console.error(`[${this.backendName}] Error updating document:`, error);
      return null;
    }
  }

  /**
   * Delete a document
   */
  async deleteDocument(id) {
    try {
      return await this.backend.deleteDocument(id);
    } catch (error) {
      console.error(`[${this.backendName}] Error deleting document:`, error);
      return false;
    }
  }

  /**
   * Toggle favorite status
   */
  async toggleFavorite(id) {
    try {
      return await this.backend.toggleFavorite(id);
    } catch (error) {
      console.error(`[${this.backendName}] Error toggling favorite:`, error);
      return null;
    }
  }

  /**
   * Clear all documents (use with caution)
   */
  async clearAllDocuments() {
    try {
      return await this.backend.clearAllDocuments();
    } catch (error) {
      console.error(`[${this.backendName}] Error clearing documents:`, error);
      return false;
    }
  }

  /**
   * Save documents (for AsyncStorage compatibility)
   */
  async saveDocuments(documents) {
    // Only AsyncStorage has this method
    if (this.backend.saveDocuments) {
      try {
        return await this.backend.saveDocuments(documents);
      } catch (error) {
        console.error(`[${this.backendName}] Error saving documents:`, error);
        return false;
      }
    }
    return true;
  }

  /**
   * Subscribe to real-time changes (Supabase only)
   */
  subscribeToChanges(callback) {
    if (this.backend.subscribeToChanges) {
      return this.backend.subscribeToChanges(callback);
    }
    return null;
  }

  /**
   * Unsubscribe from real-time changes (Supabase only)
   */
  unsubscribe(subscription) {
    if (this.backend.unsubscribe && subscription) {
      this.backend.unsubscribe(subscription);
    }
  }
}

// Export singleton instance
export default new StorageAdapter();
