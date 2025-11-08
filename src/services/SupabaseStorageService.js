import { getSupabase, isSupabaseConfigured } from '../config/supabase';
import { Document } from '../models';

const TABLE_NAME = 'documents';

const mapUpdatesToSupabase = (updates = {}) => {
  const payload = {};
  if ('title' in updates) payload.title = updates.title;
  if ('content' in updates) payload.content = updates.content;
  if ('date' in updates || 'document_date' in updates || 'documentDate' in updates) {
    payload.document_date = updates.document_date ?? updates.documentDate ?? updates.date;
  }
  if ('sourceId' in updates || 'source_id' in updates) {
    payload.source_id = updates.sourceId ?? updates.source_id;
  }
  if ('url' in updates) payload.url = updates.url;
  if ('createdAt' in updates || 'created_at' in updates) {
    payload.created_at = updates.createdAt ?? updates.created_at;
  }
  if ('isFavorite' in updates || 'is_favorite' in updates) {
    payload.is_favorite = updates.isFavorite ?? updates.is_favorite;
  }
  return payload;
};

class SupabaseStorageService {
  constructor() {
    this.tableName = TABLE_NAME;
  }

  getClient() {
    return getSupabase();
  }

  isConfigured() {
    return isSupabaseConfigured();
  }

  async getAllDocuments() {
    try {
      const supabase = this.getClient();
      const { data, error } = await supabase
        .from(this.tableName)
        .select(`
          id,
          title,
          content,
          document_date,
          url,
          created_at,
          is_favorite,
          source:sources (
            id,
            name,
            source_type,
            website_url,
            state:states (
              id,
              name,
              code,
              country:countries (
                id,
                name,
                code
              )
            )
          ),
          document_topics (
            topic:topics (
              id,
              name,
              slug
            )
          )
        `)
        .order('document_date', { ascending: false })
        .order('created_at', { ascending: false });

      if (error) {
        console.error('[Supabase] Error loading documents:', error);
        return [];
      }

      if (!Array.isArray(data)) {
        return [];
      }

      return data.map((row) => {
        const topics = Array.isArray(row.document_topics)
          ? row.document_topics
          : [];

        return Document.fromJSON({
          ...row,
          topics: topics.map((item) => item?.topic?.name).filter(Boolean),
          document_topics: topics,
          source: row.source,
          state: row.source?.state,
          country: row.source?.state?.country,
        });
      });
    } catch (error) {
      console.error('[Supabase] Error loading documents:', error);
      return [];
    }
  }

  async getDocumentById(id) {
    try {
      const supabase = this.getClient();
      const { data, error } = await supabase
        .from(this.tableName)
        .select(`
          id,
          title,
          content,
          document_date,
          url,
          created_at,
          is_favorite,
          source:sources (
            id,
            name,
            source_type,
            website_url,
            state:states (
              id,
              name,
              code,
              country:countries (
                id,
                name,
                code
              )
            )
          ),
          document_topics (
            topic:topics (
              id,
              name,
              slug
            )
          )
        `)
        .eq('id', id)
        .single();

      if (error) {
        console.error('[Supabase] Error loading document:', error);
        return null;
      }

      if (!data) {
        return null;
      }

      const topics = Array.isArray(data.document_topics) ? data.document_topics : [];

      return Document.fromJSON({
        ...data,
        topics: topics.map((item) => item?.topic?.name).filter(Boolean),
        document_topics: topics,
        source: data.source,
        state: data.source?.state,
        country: data.source?.state?.country,
      });
    } catch (error) {
      console.error('[Supabase] Error loading document:', error);
      return null;
    }
  }

  async addDocument(documentData) {
    try {
      const supabase = this.getClient();
      const document = new Document(documentData);
      const payload = document.toJSON();
      delete payload.id; // let Supabase assign UUID

      // Allow database defaults to populate created_at
      if (!documentData.createdAt && !documentData.created_at) {
        delete payload.created_at;
      }

      const { data, error } = await supabase
        .from(this.tableName)
        .insert([payload])
        .select('*')
        .single();

      if (error) {
        console.error('[Supabase] Error adding document:', error);
        return null;
      }

      return data ? await this.getDocumentById(data.id) : null;
    } catch (error) {
      console.error('[Supabase] Error adding document:', error);
      return null;
    }
  }

  async updateDocument(id, updates) {
    try {
      const supabase = this.getClient();
      const payload = mapUpdatesToSupabase(updates);
      if (Object.keys(payload).length === 0) {
        return this.getDocumentById(id);
      }

      const { data, error } = await supabase
        .from(this.tableName)
        .update(payload)
        .eq('id', id)
        .select('*')
        .single();

      if (error) {
        console.error('[Supabase] Error updating document:', error);
        return null;
      }

      return data ? await this.getDocumentById(id) : null;
    } catch (error) {
      console.error('[Supabase] Error updating document:', error);
      return null;
    }
  }

  async deleteDocument(id) {
    try {
      const supabase = this.getClient();
      const { error } = await supabase
        .from(this.tableName)
        .delete()
        .eq('id', id);

      if (error) {
        console.error('[Supabase] Error deleting document:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('[Supabase] Error deleting document:', error);
      return false;
    }
  }

  async toggleFavorite(id) {
    try {
      const document = await this.getDocumentById(id);
      if (!document) {
        return null;
      }

      const supabase = this.getClient();
      const { data, error } = await supabase
        .from(this.tableName)
        .update({ is_favorite: !document.isFavorite })
        .eq('id', id)
        .select('*')
        .single();

      if (error) {
        console.error('[Supabase] Error toggling favorite:', error);
        return null;
      }

      return data ? await this.getDocumentById(id) : null;
    } catch (error) {
      console.error('[Supabase] Error toggling favorite:', error);
      return null;
    }
  }

  subscribeToChanges(callback) {
    const supabase = this.getClient();
    return supabase
      .channel('documents_changes')
      .on('postgres_changes', { event: '*', schema: 'public', table: this.tableName }, callback)
      .subscribe();
  }

  unsubscribe(subscription) {
    if (!subscription) return;
    try {
      const supabase = this.getClient();
      supabase.removeChannel(subscription);
    } catch (error) {
      console.error('[Supabase] Error unsubscribing from changes:', error);
    }
  }

  async clearAllDocuments() {
    try {
      const supabase = this.getClient();
      const { error } = await supabase
        .from(this.tableName)
        .delete()
        .neq('id', '00000000-0000-0000-0000-000000000000');

      if (error) {
        console.error('[Supabase] Error clearing documents:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('[Supabase] Error clearing documents:', error);
      return false;
    }
  }
}

export default new SupabaseStorageService();
