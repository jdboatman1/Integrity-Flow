import React, {useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import {useDispatch, useSelector} from 'react-redux';
import Icon from 'react-native-vector-icons/Ionicons';
import {fetchEstimates} from '../store/slices/estimateSlice';
import {fetchCustomers} from '../store/slices/customerSlice';
import {colors, spacing, borderRadius, shadows} from '../theme';

const HomeScreen = ({navigation}) => {
  const dispatch = useDispatch();
  const {estimates} = useSelector(state => state.estimate);
  const {customers} = useSelector(state => state.customer);
  const {user} = useSelector(state => state.auth);
  const {isOnline, pendingEstimates} = useSelector(state => state.offline);
  const [refreshing, setRefreshing] = React.useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      await Promise.all([
        dispatch(fetchEstimates()),
        dispatch(fetchCustomers()),
      ]);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const todayEstimates = estimates.filter(est => {
    const estDate = new Date(est.custom_scheduled_date);
    const today = new Date();
    return estDate.toDateString() === today.toDateString();
  });

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }>
      {!isOnline && (
        <View style={styles.offlineBanner}>
          <Icon name="cloud-offline" size={20} color={colors.white} />
          <Text style={styles.offlineText}>
            Offline Mode - {pendingEstimates.length} pending sync
          </Text>
        </View>
      )}

      <View style={styles.header}>
        <Text style={styles.greeting}>Welcome, {user?.full_name || 'Tech'}!</Text>
        <Text style={styles.date}>{new Date().toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        })}</Text>
      </View>

      <View style={styles.statsGrid}>
        <View style={[styles.statCard, {backgroundColor: colors.primaryBlue}]}>
          <Text style={styles.statNumber}>{todayEstimates.length}</Text>
          <Text style={styles.statLabel}>Today's Jobs</Text>
        </View>

        <View style={[styles.statCard, {backgroundColor: colors.trustGreen}]}>
          <Text style={styles.statNumber}>{estimates.length}</Text>
          <Text style={styles.statLabel}>Total Estimates</Text>
        </View>

        <View style={[styles.statCard, {backgroundColor: colors.actionOrange}]}>
          <Text style={styles.statNumber}>{customers.length}</Text>
          <Text style={styles.statLabel}>Customers</Text>
        </View>
      </View>

      <View style={styles.quickActions}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Estimate')}
          testID="new-estimate-button">
          <Icon name="document-text" size={24} color={colors.primaryBlue} />
          <Text style={styles.actionButtonText}>New Estimate</Text>
          <Icon name="chevron-forward" size={20} color={colors.gray400} />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Schedule')}
          testID="view-schedule-button">
          <Icon name="calendar" size={24} color={colors.primaryBlue} />
          <Text style={styles.actionButtonText}>View Schedule</Text>
          <Icon name="chevron-forward" size={20} color={colors.gray400} />
        </TouchableOpacity>
      </View>

      <View style={styles.recentSection}>
        <Text style={styles.sectionTitle}>Today's Jobs</Text>
        {todayEstimates.length === 0 ? (
          <View style={styles.emptyState}>
            <Icon name="calendar-outline" size={48} color={colors.gray400} />
            <Text style={styles.emptyText}>No jobs scheduled for today</Text>
          </View>
        ) : (
          todayEstimates.map(estimate => (
            <TouchableOpacity
              key={estimate.name}
              style={styles.jobCard}
              testID={`job-${estimate.name}`}>
              <View style={styles.jobHeader}>
                <Text style={styles.jobCustomer}>{estimate.party_name}</Text>
                <View style={styles.jobTimeBadge}>
                  <Text style={styles.jobTime}>
                    {estimate.custom_scheduled_time || 'TBD'}
                  </Text>
                </View>
              </View>
              <Text style={styles.jobDescription}>
                {estimate.custom_service_description || 'No description'}
              </Text>
            </TouchableOpacity>
          ))
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.gray100,
  },
  offlineBanner: {
    backgroundColor: colors.warning,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.md,
    gap: spacing.sm,
  },
  offlineText: {
    color: colors.white,
    fontWeight: '600',
  },
  header: {
    backgroundColor: colors.white,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  greeting: {
    fontSize: 24,
    fontWeight: '900',
    fontStyle: 'italic',
    color: colors.gray900,
    marginBottom: spacing.xs,
  },
  date: {
    fontSize: 14,
    color: colors.gray600,
  },
  statsGrid: {
    flexDirection: 'row',
    padding: spacing.md,
    gap: spacing.md,
  },
  statCard: {
    flex: 1,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    ...shadows.md,
  },
  statNumber: {
    fontSize: 32,
    fontWeight: '900',
    color: colors.white,
    marginBottom: spacing.xs,
  },
  statLabel: {
    fontSize: 12,
    color: colors.white,
    textAlign: 'center',
  },
  quickActions: {
    backgroundColor: colors.white,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '900',
    fontStyle: 'italic',
    color: colors.gray900,
    marginBottom: spacing.md,
    textTransform: 'uppercase',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.md,
    marginBottom: spacing.sm,
  },
  actionButtonText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: colors.gray900,
    marginLeft: spacing.md,
  },
  recentSection: {
    backgroundColor: colors.white,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  emptyState: {
    alignItems: 'center',
    padding: spacing.xl,
  },
  emptyText: {
    fontSize: 14,
    color: colors.gray600,
    marginTop: spacing.md,
  },
  jobCard: {
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  jobHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  jobCustomer: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.gray900,
  },
  jobTimeBadge: {
    backgroundColor: colors.primaryBlue,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.full,
  },
  jobTime: {
    color: colors.white,
    fontSize: 12,
    fontWeight: '600',
  },
  jobDescription: {
    fontSize: 14,
    color: colors.gray600,
  },
});

export default HomeScreen;
