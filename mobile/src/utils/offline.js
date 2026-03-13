import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import {erpnextAPI} from '../api/erpnext';

export const storeOffline = async (type, data) => {
  const key = `offline_${type}_${Date.now()}`;
  await AsyncStorage.setItem(key, JSON.stringify(data));
  console.log(`Stored offline: ${key}`);
};

export const syncOfflineData = async () => {
  const state = await NetInfo.fetch();
  if (!state.isConnected) {
    console.log('Not connected - skipping sync');
    return;
  }

  // Get all offline keys
  const keys = await AsyncStorage.getAllKeys();
  const offlineKeys = keys.filter(k => k.startsWith('offline_'));

  console.log(`Syncing ${offlineKeys.length} offline items...`);

  for (const key of offlineKeys) {
    try {
      const data = await AsyncStorage.getItem(key);
      const parsedData = JSON.parse(data);

      // Sync based on type
      if (key.includes('estimate')) {
        await erpnextAPI.createQuotation(parsedData);
      }

      // Remove after successful sync
      await AsyncStorage.removeItem(key);
      console.log(`Synced and removed: ${key}`);
    } catch (error) {
      console.error(`Failed to sync ${key}:`, error);
    }
  }
};

// Set up network listener
export const setupOfflineSync = () => {
  return NetInfo.addEventListener(state => {
    if (state.isConnected) {
      syncOfflineData();
    }
  });
};
