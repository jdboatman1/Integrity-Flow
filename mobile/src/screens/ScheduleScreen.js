import React from 'react';
import {View, Text, StyleSheet, ScrollView, FlatList} from 'react-native';
import {useSelector} from 'react-redux';
import {colors, spacing, borderRadius} from '../theme';

const ScheduleScreen = () => {
  const {estimates} = useSelector(state => state.estimate);

  const scheduledEstimates = estimates
    .filter(est => est.custom_scheduled_date)
    .sort(
      (a, b) =>
        new Date(a.custom_scheduled_date) - new Date(b.custom_scheduled_date),
    );

  const renderEstimate = ({item}) => {
    const date = new Date(item.custom_scheduled_date);
    const dateStr = date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });

    return (
      <View style={styles.scheduleItem} testID={`schedule-${item.name}`}>
        <View style={styles.dateColumn}>
          <Text style={styles.dateText}>{dateStr}</Text>
          <Text style={styles.timeText}>{item.custom_scheduled_time || 'TBD'}</Text>
        </View>
        <View style={styles.detailColumn}>
          <Text style={styles.customerName}>{item.party_name}</Text>
          <Text style={styles.description} numberOfLines={2}>
            {item.custom_service_description || 'No description'}
          </Text>
          <View style={styles.statusBadge}>
            <Text style={styles.statusText}>{item.status}</Text>
          </View>
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {scheduledEstimates.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>No scheduled appointments</Text>
        </View>
      ) : (
        <FlatList
          data={scheduledEstimates}
          renderItem={renderEstimate}
          keyExtractor={item => item.name}
          contentContainerStyle={styles.list}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.gray100,
  },
  list: {
    padding: spacing.md,
  },
  scheduleItem: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  dateColumn: {
    width: 80,
    alignItems: 'center',
    justifyContent: 'center',
    borderRightWidth: 2,
    borderRightColor: colors.primaryBlue,
    marginRight: spacing.md,
  },
  dateText: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.primaryBlue,
    marginBottom: spacing.xs,
  },
  timeText: {
    fontSize: 12,
    color: colors.gray600,
  },
  detailColumn: {
    flex: 1,
  },
  customerName: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.gray900,
    marginBottom: spacing.xs,
  },
  description: {
    fontSize: 14,
    color: colors.gray600,
    marginBottom: spacing.sm,
  },
  statusBadge: {
    alignSelf: 'flex-start',
    backgroundColor: colors.gray200,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.full,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.gray700,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: colors.gray600,
  },
});

export default ScheduleScreen;
