import AsyncStorage from '@react-native-async-storage/async-storage';
import { Document } from '../models';

const STORAGE_KEY = '@TownWatch:documents';

/**
 * Service for managing document storage and retrieval
 */
class StorageService {
  /**
   * Get all documents from storage
   */
  async getAllDocuments() {
    try {
      const documentsJson = await AsyncStorage.getItem(STORAGE_KEY);
      if (documentsJson) {
        const documents = JSON.parse(documentsJson);
        return documents.map(doc => Document.fromJSON(doc));
      }
      return [];
    } catch (error) {
      console.error('Error loading documents:', error);
      return [];
    }
  }

  /**
   * Save documents to storage
   */
  async saveDocuments(documents) {
    try {
      const documentsJson = JSON.stringify(documents.map(doc => doc.toJSON()));
      await AsyncStorage.setItem(STORAGE_KEY, documentsJson);
      return true;
    } catch (error) {
      console.error('Error saving documents:', error);
      return false;
    }
  }

  /**
   * Add a new document
   */
  async addDocument(documentData) {
    try {
      const documents = await this.getAllDocuments();
      const newDocument = new Document(documentData);
      documents.push(newDocument);
      await this.saveDocuments(documents);
      return newDocument;
    } catch (error) {
      console.error('Error adding document:', error);
      return null;
    }
  }

  /**
   * Update an existing document
   */
  async updateDocument(id, updates) {
    try {
      const documents = await this.getAllDocuments();
      const index = documents.findIndex(doc => doc.id === id);
      if (index !== -1) {
        documents[index] = new Document({ ...documents[index], ...updates });
        await this.saveDocuments(documents);
        return documents[index];
      }
      return null;
    } catch (error) {
      console.error('Error updating document:', error);
      return null;
    }
  }

  /**
   * Delete a document
   */
  async deleteDocument(id) {
    try {
      const documents = await this.getAllDocuments();
      const filtered = documents.filter(doc => doc.id !== id);
      await this.saveDocuments(filtered);
      return true;
    } catch (error) {
      console.error('Error deleting document:', error);
      return false;
    }
  }

  /**
   * Toggle favorite status
   */
  async toggleFavorite(id) {
    try {
      const documents = await this.getAllDocuments();
      const document = documents.find(doc => doc.id === id);
      if (document) {
        return await this.updateDocument(id, { isFavorite: !document.isFavorite });
      }
      return null;
    } catch (error) {
      console.error('Error toggling favorite:', error);
      return null;
    }
  }

  /**
   * Clear all documents (use with caution)
   */
  async clearAllDocuments() {
    try {
      await AsyncStorage.removeItem(STORAGE_KEY);
      return true;
    } catch (error) {
      console.error('Error clearing documents:', error);
      return false;
    }
  }
}

export default new StorageService();
