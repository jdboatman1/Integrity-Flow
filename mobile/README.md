# Integrity Flow Mobile App - React Native

## Overview

Cross-platform mobile app (iOS & Android) for AAA Irrigation Service technicians to manage field operations.

## Features

### Core Features
- ✅ **Create Estimates** - Build estimates in the field with line items
- ✅ **Capture Signatures** - Digital signature capture for customer approval  
- ✅ **Photo Upload** - Attach photos to specific line items
- ✅ **GPS Tracking** - Route tracking and navigation to job sites
- ✅ **Convert to Invoice** - One-tap conversion from estimate to invoice
- ✅ **Schedule View** - Calendar view of upcoming jobs
- ✅ **Offline Mode** - Work without internet, sync when connected
- ✅ **Customer Lookup** - Search and view customer details

### Technical Stack

```json
{
  "framework": "React Native",
  "state": "Redux Toolkit",
  "navigation": "React Navigation",
  "api": "Axios + ERPNext REST API",
  "storage": "AsyncStorage + SQLite (offline)",
  "maps": "React Native Maps",
  "camera": "React Native Camera",
  "signature": "React Native Signature Canvas"
}
```

## Project Structure

```
/app/mobile/
├── android/              # Android native code
├── ios/                  # iOS native code
├── src/
│   ├── api/              # API service layer
│   │   ├── erpnext.js    # ERPNext API client
│   │   └── offline.js    # Offline sync manager
│   ├── components/       # Reusable components
│   │   ├── EstimateForm.js
│   │   ├── SignaturePad.js
│   │   ├── PhotoCapture.js
│   │   └── CustomerCard.js
│   ├── screens/          # App screens
│   │   ├── HomeScreen.js
│   │   ├── EstimateScreen.js
│   │   ├── ScheduleScreen.js
│   │   ├── CustomerDetailScreen.js
│   │   └── SettingsScreen.js
│   ├── navigation/       # Navigation config
│   │   └── AppNavigator.js
│   ├── store/            # Redux store
│   │   ├── slices/
│   │   │   ├── authSlice.js
│   │   │   ├── estimateSlice.js
│   │   │   └── customerSlice.js
│   │   └── store.js
│   ├── utils/            # Helper functions
│   │   ├── gps.js
│   │   ├── storage.js
│   │   └── validators.js
│   └── theme/            # Boatman Systems™ branding
│       ├── colors.js
│       └── fonts.js
├── App.js                # Root component
└── package.json
```

## Setup Instructions

### Prerequisites
- Node.js 16+
- React Native CLI
- Android Studio (for Android)
- Xcode (for iOS, macOS only)

### Installation

```bash
cd /app/mobile

# Install dependencies
yarn install

# iOS only (macOS)
cd ios && pod install && cd ..

# Android setup
# Open android/ in Android Studio
# Sync Gradle files
```

### Run Development

```bash
# iOS
yarn ios

# Android
yarn android
```

## ERPNext API Integration

### Authentication

```javascript
// src/api/erpnext.js
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ERPNEXT_URL = 'https://erp.aaairrigationservice.com';

export const erpnextAPI = axios.create({
  baseURL: ERPNEXT_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
erpnextAPI.interceptors.request.use(async (config) => {
  const apiKey = await AsyncStorage.getItem('api_key');
  const apiSecret = await AsyncStorage.getItem('api_secret');
  
  if (apiKey && apiSecret) {
    config.headers.Authorization = `token ${apiKey}:${apiSecret}`;
  }
  
  return config;
});
```

### API Endpoints Used

```javascript
// Customers
GET /api/resource/Customer
GET /api/resource/Customer/{id}

// Quotations (Estimates)
GET /api/resource/Quotation
POST /api/resource/Quotation
PUT /api/resource/Quotation/{id}

// Sales Invoices
GET /api/resource/Sales Invoice
POST /api/resource/Sales Invoice

// File Upload (Photos)
POST /api/method/upload_file
```

## Key Features Implementation

### 1. Create Estimate

```javascript
// src/screens/EstimateScreen.js
const createEstimate = async (estimateData) => {
  try {
    const response = await erpnextAPI.post('/api/resource/Quotation', {
      doctype: 'Quotation',
      quotation_to: 'Customer',
      party_name: estimateData.customer_id,
      custom_scheduled_date: estimateData.date,
      custom_scheduled_time: estimateData.time,
      custom_technician: estimateData.technician,
      items: estimateData.items,
    });
    
    return response.data;
  } catch (error) {
    // Store offline if no connection
    await storeOffline('estimates', estimateData);
    throw error;
  }
};
```

### 2. Capture Signature

```javascript
// src/components/SignaturePad.js
import SignatureCanvas from 'react-native-signature-canvas';

const SignaturePad = ({ onSave }) => {
  const handleSignature = (signature) => {
    // signature is base64 string
    onSave(signature);
  };
  
  return (
    <SignatureCanvas
      onOK={handleSignature}
      descriptionText="Sign above"
      clearText="Clear"
      confirmText="Save"
      webStyle={`.m-signature-pad { background-color: white; }`}
    />
  );
};
```

### 3. Photo Upload

```javascript
// src/components/PhotoCapture.js
import { launchCamera } from 'react-native-image-picker';

const capturePhoto = async (estimateId, lineItemId) => {
  const result = await launchCamera({ mediaType: 'photo', quality: 0.8 });
  
  if (result.assets) {
    const photo = result.assets[0];
    
    // Upload to ERPNext
    const formData = new FormData();
    formData.append('file', {
      uri: photo.uri,
      type: 'image/jpeg',
      name: `estimate_${estimateId}_${lineItemId}.jpg`,
    });
    formData.append('doctype', 'Quotation');
    formData.append('docname', estimateId);
    
    await erpnextAPI.post('/api/method/upload_file', formData);
  }
};
```

### 4. GPS Tracking

```javascript
// src/utils/gps.js
import Geolocation from '@react-native-community/geolocation';

export const getCurrentLocation = () => {
  return new Promise((resolve, reject) => {
    Geolocation.getCurrentPosition(
      (position) => resolve(position.coords),
      (error) => reject(error),
      { enableHighAccuracy: true, timeout: 20000 }
    );
  });
};

export const getDirections = (destination) => {
  const url = `https://www.google.com/maps/dir/?api=1&destination=${destination}`;
  Linking.openURL(url);
};
```

### 5. Offline Sync

```javascript
// src/api/offline.js
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

export const storeOffline = async (type, data) => {
  const key = `offline_${type}_${Date.now()}`;
  await AsyncStorage.setItem(key, JSON.stringify(data));
};

export const syncOfflineData = async () => {
  const isConnected = await NetInfo.fetch().then(state => state.isConnected);
  
  if (!isConnected) return;
  
  // Get all offline keys
  const keys = await AsyncStorage.getAllKeys();
  const offlineKeys = keys.filter(k => k.startsWith('offline_'));
  
  for (const key of offlineKeys) {
    const data = await AsyncStorage.getItem(key);
    const parsedData = JSON.parse(data);
    
    try {
      // Sync to ERPNext
      if (key.includes('estimates')) {
        await erpnextAPI.post('/api/resource/Quotation', parsedData);
      }
      
      // Remove after successful sync
      await AsyncStorage.removeItem(key);
    } catch (error) {
      console.error('Sync failed:', error);
    }
  }
};
```

## Boatman Systems™ Branding

```javascript
// src/theme/colors.js
export const colors = {
  primaryBlue: '#1b7abf',
  trustGreen: '#059669',
  actionOrange: '#ea580c',
  white: '#ffffff',
  gray100: '#f4f7f9',
  gray600: '#4a5568',
  gray900: '#1a202c',
};

// src/theme/fonts.js
export const fonts = {
  regular: 'Inter-Regular',
  bold: 'Inter-Bold',
  black: 'Inter-Black',
};
```

## Build for Production

### Android

```bash
cd android
./gradlew assembleRelease

# APK location:
# android/app/build/outputs/apk/release/app-release.apk
```

### iOS

```bash
# Open in Xcode
open ios/IntegrityFlow.xcworkspace

# Product > Archive
# Upload to App Store Connect
```

## Testing

```bash
# Run tests
yarn test

# Run linter
yarn lint

# Type checking (if using TypeScript)
yarn type-check
```

## Deployment

### App Stores

**Google Play Store**
- Package: `com.aaairrigation.integrityflow`
- Minimum SDK: 21 (Android 5.0)

**Apple App Store**
- Bundle ID: `com.aaairrigation.integrityflow`
- iOS Deployment Target: 12.0

## Next Steps

1. **Install React Native CLI**
2. **Initialize project**: `npx react-native init IntegrityFlow`
3. **Implement screens** following the structure above
4. **Test ERPNext API integration**
5. **Add offline sync capability**
6. **Submit to app stores**

## Support

For technical assistance:
- Email: info@aaairrigationservice.com
- Phone: 469-751-3567

**Powered by Boatman Systems™**
