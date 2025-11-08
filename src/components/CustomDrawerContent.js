import React from 'react';
import { View, StyleSheet } from 'react-native';
import { DrawerContentScrollView, DrawerItemList, DrawerItem } from '@react-navigation/drawer';
import { Text, Divider } from 'react-native-paper';
import { useTheme } from '../context/ThemeContext';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

export default function CustomDrawerContent(props) {
  const { colors } = useTheme();
  const styles = getStyles(colors);

  return (
    <DrawerContentScrollView {...props} style={styles.container}>
      <View style={styles.header}>
        <Icon name="gavel" size={48} color={colors.primary} />
        <Text style={styles.appName}>TownWatch</Text>
        <Text style={styles.subtitle}>Maryland Government Documents</Text>
      </View>

      <Divider style={styles.divider} />

      <DrawerItemList {...props} />

      <Divider style={styles.divider} />

      <View style={styles.footer}>
        <Text style={styles.version}>Version 1.0.0</Text>
      </View>
    </DrawerContentScrollView>
  );
}

const getStyles = (colors) => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  header: {
    padding: 20,
    paddingTop: 40,
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  appName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.text,
    marginTop: 12,
  },
  subtitle: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
  },
  divider: {
    marginVertical: 8,
  },
  footer: {
    padding: 20,
    marginTop: 'auto',
  },
  version: {
    fontSize: 12,
    color: colors.textTertiary,
    textAlign: 'center',
  },
});
