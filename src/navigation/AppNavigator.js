import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Import screens
import HomeScreen from '../screens/HomeScreen';
import SearchScreen from '../screens/SearchScreen';
import SettingsScreen from '../screens/SettingsScreen';
import DocumentDetailScreen from '../screens/DocumentDetailScreen';
import FilterScreen from '../screens/FilterScreen';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

// Main tab navigator (simplified - drawer removed to fix Worklets error)
function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Search') {
            iconName = focused ? 'magnify' : 'magnify';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'cog' : 'cog-outline';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6200ee',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          headerTitle: 'TownWatch',
        }}
      />
      <Tab.Screen
        name="Search"
        component={SearchScreen}
        options={{ headerTitle: 'Search Documents' }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{ headerTitle: 'Settings' }}
      />
    </Tab.Navigator>
  );
}

// Main stack navigator
export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen
          name="Main"
          component={TabNavigator}
          options={{ headerShown: false }}
        />
        <Stack.Screen
          name="DocumentDetail"
          component={DocumentDetailScreen}
          options={{ headerTitle: 'Document Details' }}
        />
        <Stack.Screen
          name="Filter"
          component={FilterScreen}
          options={{
            headerTitle: 'Filters',
            presentation: 'modal'
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
