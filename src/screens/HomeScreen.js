import React from 'react';
import { View, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import { Text, Card, Title, Paragraph, FAB, Chip, IconButton, Avatar } from 'react-native-paper';
import { useDocuments } from '../context/DocumentContext';
import { useTheme } from '../context/ThemeContext';
import SampleDataButton from '../components/SampleDataButton';
import { getDocumentIcon, getDocumentIconColor } from '../utils/documentIcons';

export default function HomeScreen({ navigation }) {
  const { filteredDocuments, loading, toggleFavorite, filterOptions, documents, refreshDocuments } = useDocuments();
  const { colors, isDark } = useTheme();

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const renderDocumentCard = ({ item }) => (
    <TouchableOpacity
      onPress={() => navigation.navigate('DocumentDetail', { documentId: item.id })}
      activeOpacity={0.7}
    >
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.cardHeader}>
            <Avatar.Icon
              size={48}
              icon={getDocumentIcon(item.source)}
              style={[styles.avatar, { backgroundColor: getDocumentIconColor(item.source) + '15' }]}
              color={getDocumentIconColor(item.source)}
            />
            <View style={styles.titleContainer}>
              <Title style={styles.title} numberOfLines={2}>{item.title}</Title>
              <IconButton
                icon={item.isFavorite ? 'heart' : 'heart-outline'}
                iconColor={item.isFavorite ? '#e91e63' : '#666'}
                size={24}
                onPress={() => toggleFavorite(item.id)}
              />
            </View>
          </View>
          <View style={styles.metadata}>
            <Text style={styles.metadataText}>{item.jurisdiction}</Text>
            <Text style={styles.metadataText}>•</Text>
            <Text style={styles.metadataText}>{item.source}</Text>
          </View>
          <Text style={styles.date}>{formatDate(item.date)}</Text>
          <Paragraph numberOfLines={3} style={styles.preview}>
            {item.content}
          </Paragraph>
          {item.topics.length > 0 && (
            <View style={styles.topicsContainer}>
              {item.topics.slice(0, 3).map((topic, index) => (
                <Chip key={index} style={styles.chip} textStyle={styles.chipText}>
                  {topic}
                </Chip>
              ))}
              {item.topics.length > 3 && (
                <Text style={styles.moreTopics}>+{item.topics.length - 3}</Text>
              )}
            </View>
          )}
        </Card.Content>
      </Card>
    </TouchableOpacity>
  );

  const EmptyState = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyText}>No documents found</Text>
      <Text style={styles.emptySubtext}>
        {filterOptions.hasActiveFilters()
          ? 'Try adjusting your filters'
          : 'Add documents to get started'}
      </Text>
      {documents.length === 0 && !filterOptions.hasActiveFilters() && (
        <SampleDataButton onDataLoaded={refreshDocuments} />
      )}
    </View>
  );

  const styles = getStyles(colors);

  return (
    <View style={styles.container}>
      <FlatList
        data={filteredDocuments}
        renderItem={renderDocumentCard}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={EmptyState}
        refreshing={loading}
      />
      <FAB
        icon="filter"
        style={styles.fab}
        onPress={() => navigation.navigate('Filter')}
        label={filterOptions.hasActiveFilters() ? 'Filters Active' : 'Filters'}
      />
    </View>
  );
}

const getStyles = (colors) => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  listContent: {
    padding: 20,
    paddingBottom: 100,
  },
  card: {
    marginBottom: 20,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    borderRadius: 12,
    backgroundColor: colors.card,
    overflow: 'hidden',
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  avatar: {
    marginRight: 12,
  },
  titleContainer: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  title: {
    fontSize: 18,
    flex: 1,
    marginRight: 8,
    color: colors.text,
  },
  metadata: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  metadataText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginRight: 8,
  },
  date: {
    fontSize: 12,
    color: colors.textTertiary,
    marginTop: 4,
    marginBottom: 8,
  },
  preview: {
    fontSize: 14,
    color: colors.text,
    lineHeight: 20,
  },
  topicsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
    alignItems: 'center',
  },
  chip: {
    marginRight: 8,
    marginBottom: 4,
    height: 28,
  },
  chipText: {
    fontSize: 12,
  },
  moreTopics: {
    fontSize: 12,
    color: colors.textSecondary,
    marginLeft: 4,
  },
  fab: {
    position: 'absolute',
    right: 16,
    bottom: 16,
    backgroundColor: colors.primary,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 100,
  },
  emptyText: {
    fontSize: 18,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: colors.textTertiary,
  },
});
