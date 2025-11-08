import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Linking } from 'react-native';
import { Text, Title, Chip, IconButton, Button } from 'react-native-paper';
import { useDocuments } from '../context/DocumentContext';

export default function DocumentDetailScreen({ route, navigation }) {
  const { documentId } = route.params;
  const { documents, toggleFavorite } = useDocuments();
  const [document, setDocument] = useState(null);

  useEffect(() => {
    const doc = documents.find(d => d.id === documentId);
    setDocument(doc);
  }, [documentId, documents]);

  if (!document) {
    return (
      <View style={styles.container}>
        <Text>Document not found</Text>
      </View>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleOpenUrl = () => {
    if (document.url) {
      Linking.openURL(document.url);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Title style={styles.title}>{document.title}</Title>
        <IconButton
          icon={document.isFavorite ? 'heart' : 'heart-outline'}
          iconColor={document.isFavorite ? '#e91e63' : '#666'}
          size={28}
          onPress={() => toggleFavorite(document.id)}
        />
      </View>

      <View style={styles.metadataSection}>
        <View style={styles.metadataRow}>
          <Text style={styles.metadataLabel}>Date:</Text>
          <Text style={styles.metadataValue}>{formatDate(document.date)}</Text>
        </View>
        <View style={styles.metadataRow}>
          <Text style={styles.metadataLabel}>Jurisdiction:</Text>
          <Text style={styles.metadataValue}>{document.jurisdiction}</Text>
        </View>
        <View style={styles.metadataRow}>
          <Text style={styles.metadataLabel}>Source:</Text>
          <Text style={styles.metadataValue}>{document.source}</Text>
        </View>
      </View>

      {document.topics.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Topics</Text>
          <View style={styles.topicsContainer}>
            {document.topics.map((topic, index) => (
              <Chip key={index} style={styles.chip}>
                {topic}
              </Chip>
            ))}
          </View>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Content</Text>
        <Text style={styles.content}>{document.content}</Text>
      </View>

      {document.url && (
        <Button
          mode="outlined"
          onPress={handleOpenUrl}
          style={styles.urlButton}
          icon="open-in-new"
        >
          View Original Source
        </Button>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  title: {
    fontSize: 24,
    flex: 1,
    marginRight: 8,
  },
  metadataSection: {
    backgroundColor: '#f5f5f5',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  metadataRow: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  metadataLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#666',
    width: 100,
  },
  metadataValue: {
    fontSize: 14,
    color: '#333',
    flex: 1,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333',
  },
  topicsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  chip: {
    marginRight: 8,
    marginBottom: 8,
  },
  contentText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
  },
  urlButton: {
    marginTop: 16,
    marginBottom: 32,
  },
});
