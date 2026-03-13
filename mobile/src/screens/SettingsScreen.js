import React from 'react';
import {View, Text, StyleSheet, TouchableOpacity, Alert} from 'react-native';
import {useDispatch, useSelector} from 'react-redux';
import Icon from 'react-native-vector-icons/Ionicons';
import {logout} from '../store/slices/authSlice';
import {colors, spacing, borderRadius} from '../theme';

const SettingsScreen = ({navigation}) => {
  const dispatch = useDispatch();
  const {user} = useSelector(state => state.auth);
  const {isOnline, pendingEstimates} = useSelector(state => state.offline);

  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      {text: 'Cancel', style: 'cancel'},
      {
        text: 'Logout',
        style: 'destructive',
        onPress: async () => {
          await dispatch(logout());
          navigation.replace('Login');
        },
      },
    ]);
  };

  return (
    <View style={styles.container}>
      <View style={styles.userSection}>
        <View style={styles.avatar}>
          <Icon name="person" size={40} color={colors.white} />
        </View>
        <Text style={styles.userName}>{user?.full_name || 'Technician'}</Text>
        <Text style={styles.userEmail}>{user?.email || ''}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Status</Text>
        <View style={styles.statusCard}>
          <Icon
            name={isOnline ? 'cloud-done' : 'cloud-offline'}
            size={24}
            color={isOnline ? colors.trustGreen : colors.warning}
          />
          <Text style={styles.statusText}>
            {isOnline ? 'Online' : 'Offline'}
          </Text>
          {pendingEstimates.length > 0 && (
            <View style={styles.pendingBadge}>
              <Text style={styles.pendingText}>
                {pendingEstimates.length} pending
              </Text>
            </View>
          )}
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Actions</Text>
        <TouchableOpacity style={styles.actionButton} testID="logout-button" onPress={handleLogout}>
          <Icon name="log-out" size={20} color={colors.error} />
          <Text style={[styles.actionText, {color: colors.error}]}>Logout</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.footer}>Powered by Boatman Systems™</Text>
      <Text style={styles.version}>Version 1.0.0</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.gray100,
  },
  userSection: {
    backgroundColor: colors.primaryBlue,
    alignItems: 'center',
    padding: spacing.xl,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.white + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  userName: {
    fontSize: 20,
    fontWeight: '900',
    fontStyle: 'italic',
    color: colors.white,
    marginBottom: spacing.xs,
  },
  userEmail: {
    fontSize: 14,
    color: colors.white,
    opacity: 0.8,
  },
  section: {
    backgroundColor: colors.white,
    padding: spacing.lg,
    marginTop: spacing.md,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.gray600,
    marginBottom: spacing.md,
    textTransform: 'uppercase',
  },
  statusCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.md,
    gap: spacing.md,
  },
  statusText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: colors.gray900,
  },
  pendingBadge: {
    backgroundColor: colors.warning,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.full,
  },
  pendingText: {
    color: colors.white,
    fontSize: 12,
    fontWeight: '700',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.md,
    gap: spacing.md,
  },
  actionText: {
    fontSize: 16,
    fontWeight: '600',
  },
  footer: {
    textAlign: 'center',
    fontSize: 12,
    fontStyle: 'italic',
    color: colors.gray600,
    marginTop: spacing.xl,
  },
  version: {
    textAlign: 'center',
    fontSize: 12,
    color: colors.gray400,
    marginTop: spacing.xs,
  },
});

export default SettingsScreen;
