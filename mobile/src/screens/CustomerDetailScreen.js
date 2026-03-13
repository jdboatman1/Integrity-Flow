import React from 'react';
import {View, Text, StyleSheet} from 'react-native';
import {colors, spacing} from '../theme';

const CustomerDetailScreen = ({route}) => {
  const {customer} = route.params || {};

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Customer Details</Text>
      <Text>Coming soon...</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: spacing.lg,
    backgroundColor: colors.white,
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    marginBottom: spacing.md,
  },
});

export default CustomerDetailScreen;
