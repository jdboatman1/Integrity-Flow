import Geolocation from '@react-native-community/geolocation';
import {Linking} from 'react-native';

export const getCurrentLocation = () => {
  return new Promise((resolve, reject) => {
    Geolocation.getCurrentPosition(
      position => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
      },
      error => reject(error),
      {
        enableHighAccuracy: true,
        timeout: 20000,
        maximumAge: 1000,
      },
    );
  });
};

export const openGoogleMaps = address => {
  const url = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(
    address,
  )}`;
  Linking.openURL(url);
};

export const openWaze = address => {
  const url = `https://waze.com/ul?q=${encodeURIComponent(address)}`;
  Linking.openURL(url);
};

export const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371; // Radius of the earth in km
  const dLat = deg2rad(lat2 - lat1);
  const dLon = deg2rad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(deg2rad(lat1)) *
      Math.cos(deg2rad(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const d = R * c; // Distance in km
  return d * 0.621371; // Convert to miles
};

const deg2rad = deg => {
  return deg * (Math.PI / 180);
};
