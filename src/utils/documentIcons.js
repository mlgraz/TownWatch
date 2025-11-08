/**
 * Document icon utility
 * Returns appropriate icon name based on document source/type
 */

export const getDocumentIcon = (source) => {
  const sourceLower = source.toLowerCase();

  // Legislature icons
  if (sourceLower.includes('general assembly') ||
      sourceLower.includes('legislature') ||
      sourceLower.includes('senate') ||
      sourceLower.includes('house')) {
    return 'gavel';
  }

  // Council icons
  if (sourceLower.includes('council') ||
      sourceLower.includes('city council') ||
      sourceLower.includes('county council')) {
    return 'account-group';
  }

  // Board/Commission icons
  if (sourceLower.includes('board') ||
      sourceLower.includes('commission')) {
    return 'clipboard-text';
  }

  // Planning icons
  if (sourceLower.includes('planning')) {
    return 'city';
  }

  // Transportation icons
  if (sourceLower.includes('transportation') ||
      sourceLower.includes('transit')) {
    return 'train-car';
  }

  // Budget/Finance icons
  if (sourceLower.includes('budget') ||
      sourceLower.includes('finance') ||
      sourceLower.includes('comptroller') ||
      sourceLower.includes('estimates')) {
    return 'cash-multiple';
  }

  // Default icon
  return 'file-document';
};

export const getDocumentIconColor = (source) => {
  const sourceLower = source.toLowerCase();

  // Legislature - purple
  if (sourceLower.includes('general assembly') ||
      sourceLower.includes('legislature') ||
      sourceLower.includes('senate') ||
      sourceLower.includes('house')) {
    return '#6200ee';
  }

  // Council - blue
  if (sourceLower.includes('council')) {
    return '#1976d2';
  }

  // Board/Commission - teal
  if (sourceLower.includes('board') ||
      sourceLower.includes('commission')) {
    return '#00897b';
  }

  // Planning - green
  if (sourceLower.includes('planning')) {
    return '#43a047';
  }

  // Transportation - orange
  if (sourceLower.includes('transportation') ||
      sourceLower.includes('transit')) {
    return '#fb8c00';
  }

  // Budget/Finance - red
  if (sourceLower.includes('budget') ||
      sourceLower.includes('finance') ||
      sourceLower.includes('comptroller') ||
      sourceLower.includes('estimates')) {
    return '#e53935';
  }

  // Default - gray
  return '#757575';
};

export const getTopicIcon = (topic) => {
  const topicLower = topic.toLowerCase();

  const topicIcons = {
    'budget': 'cash',
    'finance': 'cash',
    'housing': 'home',
    'development': 'domain',
    'transportation': 'car',
    'transit': 'bus',
    'environment': 'leaf',
    'climate': 'weather-partly-cloudy',
    'sustainability': 'recycle',
    'public safety': 'shield',
    'police': 'police-badge',
    'fire': 'fire',
    'education': 'school',
    'health': 'hospital',
    'healthcare': 'medical-bag',
    'planning': 'floor-plan',
    'zoning': 'map',
    'legislation': 'gavel',
    'contracts': 'file-sign',
    'procurement': 'cart',
  };

  for (const [key, icon] of Object.entries(topicIcons)) {
    if (topicLower.includes(key)) {
      return icon;
    }
  }

  return 'tag';
};
