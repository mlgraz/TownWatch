/**
 * Document model representing a government meeting note or policy document
 */

export class Document {
  constructor(params = {}) {
    const {
      id,
      title,
      content,
      date,
      document_date,
      documentDate,
      source,
      source_name,
      sourceName,
      source_id,
      sourceId,
      source_type,
      sourceType,
      jurisdiction,
      state,
      state_name,
      stateName,
      state_code,
      stateCode,
      country,
      country_name,
      countryName,
      topics = [],
      document_topics,
      url = null,
      createdAt,
      created_at,
      scraped_at,
      isFavorite,
      is_favorite,
    } = params;

    this.id = id || this.generateId();
    this.title = title;
    this.content = content;
    this.date = date || document_date || documentDate || null;

    this.sourceId = source_id ?? sourceId ?? null;
    this.sourceType = source_type ?? sourceType ?? null;

    const sourceObject = typeof source === 'string' ? { name: source } : source || {};
    this.source = sourceObject.name ?? source_name ?? sourceName ?? null;

    const stateObject =
      state ||
      sourceObject.state ||
      (state_name || stateName || state_code || stateCode
        ? {
            name: state_name ?? stateName ?? null,
            code: state_code ?? stateCode ?? null,
          }
        : null);

    const countryObject =
      country ||
      stateObject?.country ||
      (country_name || countryName
        ? {
            name: country_name ?? countryName ?? null,
          }
        : null);

    this.state = stateObject || null;
    this.country = countryObject || null;

    const jurisdictionParts = [];
    if (stateObject?.name) {
      jurisdictionParts.push(stateObject.name);
    }
    if (countryObject?.name && countryObject.name !== stateObject?.name) {
      jurisdictionParts.push(countryObject.name);
    }
    this.jurisdiction = jurisdiction ?? jurisdictionParts.join(', ');

    this.topics = Document.normalizeTopics(topics, document_topics);
    this.url = url;
    this.createdAt = createdAt || created_at || scraped_at || new Date().toISOString();
    this.isFavorite = typeof isFavorite === 'boolean' ? isFavorite : Boolean(is_favorite);
  }

  generateId() {
    return `doc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  static normalizeTopics(explicitTopics, relatedTopics) {
    const collected = [];

    const addTopic = (topic) => {
      if (!topic) {
        return;
      }

      if (typeof topic === 'string') {
        collected.push(topic);
        return;
      }

      if (topic.name) {
        collected.push(topic.name);
        return;
      }

      if (topic.topic) {
        addTopic(topic.topic);
      }
    };

    if (Array.isArray(explicitTopics)) {
      explicitTopics.forEach(addTopic);
    }

    if (Array.isArray(relatedTopics)) {
      relatedTopics.forEach(addTopic);
    }

    return collected.filter((value, index, array) => array.indexOf(value) === index);
  }

  toJSON() {
    const json = {
      title: this.title,
      content: this.content,
      document_date: this.date,
      source_id: this.sourceId,
      source_type: this.sourceType,
      jurisdiction: this.jurisdiction,
      topics: this.topics,
      url: this.url,
      created_at: this.createdAt,
      is_favorite: this.isFavorite,
    };

    if (this.source) {
      json.source = this.source;
    }

    if (this.id) {
      json.id = this.id;
    }

    if (!json.document_date && this.date) {
      json.document_date = this.date;
    }

    return json;
  }

  static fromJSON(json) {
    return new Document(json);
  }
}
