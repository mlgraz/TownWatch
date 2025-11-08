import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { Button, Dialog, Portal, Paragraph } from 'react-native-paper';
import StorageService from '../services/StorageService';
import { loadSampleData } from '../utils/sampleData';

export default function SampleDataButton({ onDataLoaded }) {
  const [dialogVisible, setDialogVisible] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLoadSampleData = async () => {
    setLoading(true);
    const success = await loadSampleData(StorageService);
    setLoading(false);
    setDialogVisible(false);

    if (success && onDataLoaded) {
      onDataLoaded();
    }
  };

  return (
    <View style={styles.container}>
      <Button
        mode="outlined"
        onPress={() => setDialogVisible(true)}
        icon="download"
      >
        Load Sample Data
      </Button>

      <Portal>
        <Dialog visible={dialogVisible} onDismiss={() => setDialogVisible(false)}>
          <Dialog.Title>Load Sample Data</Dialog.Title>
          <Dialog.Content>
            <Paragraph>
              This will add 6 sample government meeting documents to the app for testing purposes.
              This is useful to see how the app works with real data.
            </Paragraph>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setDialogVisible(false)} disabled={loading}>
              Cancel
            </Button>
            <Button onPress={handleLoadSampleData} loading={loading}>
              Load
            </Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    margin: 16,
  },
});
