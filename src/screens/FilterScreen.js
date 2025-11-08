import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Button, Chip, Switch, Divider } from 'react-native-paper';
import { useDocuments } from '../context/DocumentContext';

export default function FilterScreen({ navigation }) {
  const {
    filterOptions,
    updateFilters,
    resetFilters,
    getAllTopics,
    getAllJurisdictions,
    getAllSources,
  } = useDocuments();

  const [selectedTopics, setSelectedTopics] = useState(filterOptions.selectedTopics);
  const [selectedJurisdictions, setSelectedJurisdictions] = useState(filterOptions.jurisdictions);
  const [selectedSources, setSelectedSources] = useState(filterOptions.sources);
  const [favoritesOnly, setFavoritesOnly] = useState(filterOptions.favoritesOnly);

  const allTopics = getAllTopics();
  const allJurisdictions = getAllJurisdictions();
  const allSources = getAllSources();

  const toggleTopic = (topic) => {
    setSelectedTopics(prev =>
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    );
  };

  const toggleJurisdiction = (jurisdiction) => {
    setSelectedJurisdictions(prev =>
      prev.includes(jurisdiction)
        ? prev.filter(j => j !== jurisdiction)
        : [...prev, jurisdiction]
    );
  };

  const toggleSource = (source) => {
    setSelectedSources(prev =>
      prev.includes(source)
        ? prev.filter(s => s !== source)
        : [...prev, source]
    );
  };

  const handleApply = () => {
    updateFilters({
      ...filterOptions,
      selectedTopics,
      jurisdictions: selectedJurisdictions,
      sources: selectedSources,
      favoritesOnly,
    });
    navigation.goBack();
  };

  const handleReset = () => {
    setSelectedTopics([]);
    setSelectedJurisdictions([]);
    setSelectedSources([]);
    setFavoritesOnly(false);
    resetFilters();
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        {/* Favorites Filter */}
        <View style={styles.section}>
          <View style={styles.switchRow}>
            <Text style={styles.sectionTitle}>Favorites Only</Text>
            <Switch
              value={favoritesOnly}
              onValueChange={setFavoritesOnly}
              color="#6200ee"
            />
          </View>
        </View>

        <Divider style={styles.divider} />

        {/* Topics Filter */}
        {allTopics.length > 0 && (
          <>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Topics</Text>
              <View style={styles.chipsContainer}>
                {allTopics.map((topic) => (
                  <Chip
                    key={topic}
                    selected={selectedTopics.includes(topic)}
                    onPress={() => toggleTopic(topic)}
                    style={[
                      styles.chip,
                      selectedTopics.includes(topic) && styles.selectedChip
                    ]}
                    selectedColor={selectedTopics.includes(topic) ? '#fff' : '#333'}
                  >
                    {topic}
                  </Chip>
                ))}
              </View>
            </View>
            <Divider style={styles.divider} />
          </>
        )}

        {/* Jurisdictions Filter */}
        {allJurisdictions.length > 0 && (
          <>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Jurisdictions</Text>
              <View style={styles.chipsContainer}>
                {allJurisdictions.map((jurisdiction) => (
                  <Chip
                    key={jurisdiction}
                    selected={selectedJurisdictions.includes(jurisdiction)}
                    onPress={() => toggleJurisdiction(jurisdiction)}
                    style={[
                      styles.chip,
                      selectedJurisdictions.includes(jurisdiction) && styles.selectedChip
                    ]}
                    selectedColor={selectedJurisdictions.includes(jurisdiction) ? '#fff' : '#333'}
                  >
                    {jurisdiction}
                  </Chip>
                ))}
              </View>
            </View>
            <Divider style={styles.divider} />
          </>
        )}

        {/* Sources Filter */}
        {allSources.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Sources</Text>
            <View style={styles.chipsContainer}>
              {allSources.map((source) => (
                <Chip
                  key={source}
                  selected={selectedSources.includes(source)}
                  onPress={() => toggleSource(source)}
                  style={[
                    styles.chip,
                    selectedSources.includes(source) && styles.selectedChip
                  ]}
                  selectedColor={selectedSources.includes(source) ? '#fff' : '#333'}
                >
                  {source}
                </Chip>
              ))}
            </View>
          </View>
        )}
      </ScrollView>

      <View style={styles.footer}>
        <Button
          mode="outlined"
          onPress={handleReset}
          style={styles.resetButton}
        >
          Reset
        </Button>
        <Button
          mode="contained"
          onPress={handleApply}
          style={styles.applyButton}
        >
          Apply Filters
        </Button>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  section: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333',
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  chipsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  chip: {
    marginRight: 8,
    marginBottom: 8,
  },
  selectedChip: {
    backgroundColor: '#6200ee',
  },
  divider: {
    marginVertical: 16,
  },
  footer: {
    flexDirection: 'row',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    backgroundColor: '#fff',
  },
  resetButton: {
    flex: 1,
    marginRight: 8,
  },
  applyButton: {
    flex: 1,
    marginLeft: 8,
    backgroundColor: '#6200ee',
  },
});
