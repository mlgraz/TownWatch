import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { List, Divider, Text, Menu } from 'react-native-paper';
import { useTheme } from '../context/ThemeContext';

export default function SettingsScreen() {
  const { colors, isDark, themeMode, setTheme } = useTheme();
  const [menuVisible, setMenuVisible] = useState(false);

  const styles = getStyles(colors);

  const getThemeLabel = (mode) => {
    switch (mode) {
      case 'light':
        return 'Light';
      case 'dark':
        return 'Dark';
      case 'auto':
        return 'Auto (System)';
      default:
        return 'Auto (System)';
    }
  };

  const getThemeIcon = (mode) => {
    switch (mode) {
      case 'light':
        return 'white-balance-sunny';
      case 'dark':
        return 'moon-waning-crescent';
      case 'auto':
        return 'theme-light-dark';
      default:
        return 'theme-light-dark';
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Appearance</Text>

        <Menu
          visible={menuVisible}
          onDismiss={() => setMenuVisible(false)}
          anchor={
            <List.Item
              title="Theme"
              description={getThemeLabel(themeMode)}
              left={(props) => <List.Icon {...props} icon={getThemeIcon(themeMode)} />}
              right={(props) => <List.Icon {...props} icon="chevron-down" />}
              onPress={() => setMenuVisible(true)}
            />
          }
        >
          <Menu.Item
            onPress={() => {
              setTheme('light');
              setMenuVisible(false);
            }}
            title="Light"
            leadingIcon="white-balance-sunny"
            trailingIcon={themeMode === 'light' ? 'check' : undefined}
          />
          <Menu.Item
            onPress={() => {
              setTheme('dark');
              setMenuVisible(false);
            }}
            title="Dark"
            leadingIcon="moon-waning-crescent"
            trailingIcon={themeMode === 'dark' ? 'check' : undefined}
          />
          <Menu.Item
            onPress={() => {
              setTheme('auto');
              setMenuVisible(false);
            }}
            title="Auto (System)"
            leadingIcon="theme-light-dark"
            trailingIcon={themeMode === 'auto' ? 'check' : undefined}
          />
        </Menu>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <List.Item
          title="TownWatch"
          description="Maryland Government Documents Aggregator"
          left={(props) => <List.Icon {...props} icon="information" />}
        />
        <Divider />
        <List.Item
          title="Version"
          description="1.0.0"
          left={(props) => <List.Icon {...props} icon="tag" />}
        />
      </View>
    </ScrollView>
  );
}

const getStyles = (colors) => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  section: {
    marginTop: 16,
    backgroundColor: colors.surface,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: colors.primary,
    paddingHorizontal: 16,
    paddingVertical: 12,
    textTransform: 'uppercase',
  },
});
