import React, {useEffect} from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {Provider} from 'react-redux';
import Icon from 'react-native-vector-icons/Ionicons';
import {store} from './store';
import {colors} from './theme';

// Screens
import LoginScreen from './screens/LoginScreen';
import HomeScreen from './screens/HomeScreen';
import EstimateScreen from './screens/EstimateScreen';
import ScheduleScreen from './screens/ScheduleScreen';
import CustomerDetailScreen from './screens/CustomerDetailScreen';
import SettingsScreen from './screens/SettingsScreen';
import SignatureScreen from './screens/SignatureScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        tabBarIcon: ({focused, color, size}) => {
          let iconName;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Schedule') {
            iconName = focused ? 'calendar' : 'calendar-outline';
          } else if (route.name === 'Estimate') {
            iconName = focused ? 'document-text' : 'document-text-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: colors.primaryBlue,
        tabBarInactiveTintColor: colors.gray600,
        headerStyle: {
          backgroundColor: colors.primaryBlue,
        },
        headerTintColor: colors.white,
        headerTitleStyle: {
          fontWeight: '900',
          fontStyle: 'italic',
          textTransform: 'uppercase',
        },
      })}>
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{title: 'AAA Irrigation'}}
      />
      <Tab.Screen name="Schedule" component={ScheduleScreen} />
      <Tab.Screen
        name="Estimate"
        component={EstimateScreen}
        options={{title: 'New Estimate'}}
      />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

function App() {
  return (
    <Provider store={store}>
      <NavigationContainer>
        <Stack.Navigator
          screenOptions={{
            headerStyle: {
              backgroundColor: colors.primaryBlue,
            },
            headerTintColor: colors.white,
            headerTitleStyle: {
              fontWeight: '900',
              fontStyle: 'italic',
              textTransform: 'uppercase',
            },
          }}>
          <Stack.Screen
            name="Login"
            component={LoginScreen}
            options={{headerShown: false}}
          />
          <Stack.Screen
            name="Main"
            component={MainTabs}
            options={{headerShown: false}}
          />
          <Stack.Screen
            name="CustomerDetail"
            component={CustomerDetailScreen}
            options={{title: 'Customer Details'}}
          />
          <Stack.Screen
            name="Signature"
            component={SignatureScreen}
            options={{title: 'Capture Signature'}}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </Provider>
  );
}

export default App;
