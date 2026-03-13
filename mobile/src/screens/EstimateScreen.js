import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import {useDispatch, useSelector} from 'react-redux';
import Icon from 'react-native-vector-icons/Ionicons';
import {
  createEstimate,
  addLineItem,
  removeLineItem,
  clearCurrentEstimate,
} from '../store/slices/estimateSlice';
import {fetchCustomers} from '../store/slices/customerSlice';
import {colors, spacing, borderRadius, shadows} from '../theme';
import PhotoCapture from '../components/PhotoCapture';

const EstimateScreen = ({navigation}) => {
  const dispatch = useDispatch();
  const {customers, loading: customerLoading} = useSelector(
    state => state.customer,
  );
  const {currentEstimate, loading} = useSelector(state => state.estimate);

  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [serviceDescription, setServiceDescription] = useState('');
  const [scheduledDate, setScheduledDate] = useState('');
  const [scheduledTime, setScheduledTime] = useState('9AM-11AM');
  const [lineItemDesc, setLineItemDesc] = useState('');
  const [lineItemQty, setLineItemQty] = useState('1');
  const [lineItemRate, setLineItemRate] = useState('');
  const [showCustomerPicker, setShowCustomerPicker] = useState(false);

  useEffect(() => {
    if (customers.length === 0) {
      dispatch(fetchCustomers());
    }
  }, []);

  const handleAddLineItem = () => {
    if (!lineItemDesc || !lineItemRate) {
      Alert.alert('Error', 'Please enter description and rate');
      return;
    }

    const lineItem = {
      item_code: lineItemDesc,
      item_name: lineItemDesc,
      qty: parseFloat(lineItemQty) || 1,
      rate: parseFloat(lineItemRate),
      description: lineItemDesc,
    };

    dispatch(addLineItem(lineItem));
    setLineItemDesc('');
    setLineItemQty('1');
    setLineItemRate('');
  };

  const handleRemoveLineItem = index => {
    dispatch(removeLineItem(index));
  };

  const handleCaptureSignature = () => {
    navigation.navigate('Signature', {
      onSignatureSaved: signature => {
        // Signature will be saved in estimate
        console.log('Signature captured:', signature);
      },
    });
  };

  const handleCreateEstimate = async () => {
    if (!selectedCustomer) {
      Alert.alert('Error', 'Please select a customer');
      return;
    }

    if (!currentEstimate?.items || currentEstimate.items.length === 0) {
      Alert.alert('Error', 'Please add at least one line item');
      return;
    }

    const estimateData = {
      doctype: 'Quotation',
      quotation_to: 'Customer',
      party_name: selectedCustomer.name,
      transaction_date: new Date().toISOString().split('T')[0],
      custom_scheduled_date: scheduledDate || new Date().toISOString().split('T')[0],
      custom_scheduled_time: scheduledTime,
      custom_service_description: serviceDescription,
      items: currentEstimate.items,
    };

    try {
      await dispatch(createEstimate(estimateData)).unwrap();
      Alert.alert('Success', 'Estimate created successfully!', [
        {
          text: 'OK',
          onPress: () => {
            dispatch(clearCurrentEstimate());
            setSelectedCustomer(null);
            setServiceDescription('');
            navigation.navigate('Home');
          },
        },
      ]);
    } catch (error) {
      if (error.includes('offline')) {
        Alert.alert('Saved Offline', 'Estimate will sync when online');
      } else {
        Alert.alert('Error', error);
      }
    }
  };

  const totalAmount = currentEstimate?.items?.reduce(
    (sum, item) => sum + item.qty * item.rate,
    0,
  ) || 0;

  return (
    <ScrollView style={styles.container}>
      {/* Customer Selection */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Customer</Text>
        <TouchableOpacity
          style={styles.customerSelector}
          onPress={() => setShowCustomerPicker(!showCustomerPicker)}
          testID="customer-selector">
          <Icon name="person" size={20} color={colors.primaryBlue} />
          <Text style={styles.customerSelectorText}>
            {selectedCustomer
              ? selectedCustomer.customer_name
              : 'Select Customer'}
          </Text>
          <Icon name="chevron-down" size={20} color={colors.gray400} />
        </TouchableOpacity>

        {showCustomerPicker && (
          <View style={styles.customerList}>
            {customerLoading ? (
              <ActivityIndicator color={colors.primaryBlue} />
            ) : (
              customers.map(customer => (
                <TouchableOpacity
                  key={customer.name}
                  style={styles.customerItem}
                  onPress={() => {
                    setSelectedCustomer(customer);
                    setShowCustomerPicker(false);
                  }}
                  testID={`customer-${customer.name}`}>
                  <Text style={styles.customerItemText}>
                    {customer.customer_name}
                  </Text>
                  <Text style={styles.customerItemPhone}>
                    {customer.mobile_no}
                  </Text>
                </TouchableOpacity>
              ))
            )}
          </View>
        )}
      </View>

      {/* Schedule */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Schedule</Text>
        <View style={styles.row}>
          <View style={styles.halfInput}>
            <Text style={styles.label}>Date</Text>
            <TextInput
              style={styles.input}
              value={scheduledDate}
              onChangeText={setScheduledDate}
              placeholder="YYYY-MM-DD"
              placeholderTextColor={colors.gray400}
              testID="schedule-date"
            />
          </View>
          <View style={styles.halfInput}>
            <Text style={styles.label}>Time</Text>
            <TextInput
              style={styles.input}
              value={scheduledTime}
              onChangeText={setScheduledTime}
              placeholder="9AM-11AM"
              placeholderTextColor={colors.gray400}
              testID="schedule-time"
            />
          </View>
        </View>
      </View>

      {/* Service Description */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Service Description</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          value={serviceDescription}
          onChangeText={setServiceDescription}
          placeholder="Describe the service needed..."
          placeholderTextColor={colors.gray400}
          multiline
          numberOfLines={4}
          testID="service-description"
        />
      </View>

      {/* Line Items */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Line Items</Text>

        {currentEstimate?.items?.map((item, index) => (
          <View key={index} style={styles.lineItem} testID={`line-item-${index}`}>
            <View style={styles.lineItemInfo}>
              <Text style={styles.lineItemDesc}>{item.description}</Text>
              <Text style={styles.lineItemAmount}>
                {item.qty} x ${item.rate.toFixed(2)} = $
                {(item.qty * item.rate).toFixed(2)}
              </Text>
            </View>
            <TouchableOpacity
              onPress={() => handleRemoveLineItem(index)}
              testID={`remove-item-${index}`}>
              <Icon name="trash" size={20} color={colors.error} />
            </TouchableOpacity>
          </View>
        ))}

        <View style={styles.addLineItem}>
          <TextInput
            style={[styles.input, {marginBottom: spacing.sm}]}
            value={lineItemDesc}
            onChangeText={setLineItemDesc}
            placeholder="Item description"
            placeholderTextColor={colors.gray400}
            testID="line-item-description"
          />
          <View style={styles.row}>
            <View style={styles.thirdInput}>
              <TextInput
                style={styles.input}
                value={lineItemQty}
                onChangeText={setLineItemQty}
                placeholder="Qty"
                keyboardType="numeric"
                placeholderTextColor={colors.gray400}
                testID="line-item-qty"
              />
            </View>
            <View style={styles.thirdInput}>
              <TextInput
                style={styles.input}
                value={lineItemRate}
                onChangeText={setLineItemRate}
                placeholder="Rate"
                keyboardType="numeric"
                placeholderTextColor={colors.gray400}
                testID="line-item-rate"
              />
            </View>
            <View style={styles.thirdInput}>
              <TouchableOpacity
                style={styles.addButton}
                onPress={handleAddLineItem}
                testID="add-line-item-button">
                <Icon name="add" size={24} color={colors.white} />
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </View>

      {/* Total */}
      <View style={styles.totalSection}>
        <Text style={styles.totalLabel}>Total Amount:</Text>
        <Text style={styles.totalAmount}>${totalAmount.toFixed(2)}</Text>
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={handleCaptureSignature}
          testID="capture-signature-button">
          <Icon name="create" size={20} color={colors.primaryBlue} />
          <Text style={styles.secondaryButtonText}>Capture Signature</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.primaryButton}
          onPress={handleCreateEstimate}
          disabled={loading}
          testID="create-estimate-button">
          {loading ? (
            <ActivityIndicator color={colors.white} />
          ) : (
            <Text style={styles.primaryButtonText}>Create Estimate</Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.gray100,
  },
  section: {
    backgroundColor: colors.white,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '900',
    fontStyle: 'italic',
    color: colors.gray900,
    marginBottom: spacing.md,
    textTransform: 'uppercase',
  },
  customerSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.md,
    gap: spacing.sm,
  },
  customerSelectorText: {
    flex: 1,
    fontSize: 16,
    color: colors.gray900,
  },
  customerList: {
    marginTop: spacing.md,
    borderRadius: borderRadius.md,
    backgroundColor: colors.gray100,
    maxHeight: 200,
  },
  customerItem: {
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray200,
  },
  customerItemText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.gray900,
  },
  customerItemPhone: {
    fontSize: 14,
    color: colors.gray600,
    marginTop: spacing.xs,
  },
  row: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  halfInput: {
    flex: 1,
  },
  thirdInput: {
    flex: 1,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.gray700,
    marginBottom: spacing.xs,
  },
  input: {
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    fontSize: 16,
    color: colors.gray900,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  lineItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.md,
    marginBottom: spacing.sm,
  },
  lineItemInfo: {
    flex: 1,
  },
  lineItemDesc: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.gray900,
    marginBottom: spacing.xs,
  },
  lineItemAmount: {
    fontSize: 14,
    color: colors.gray600,
  },
  addLineItem: {
    marginTop: spacing.md,
  },
  addButton: {
    backgroundColor: colors.trustGreen,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
    height: 48,
  },
  totalSection: {
    backgroundColor: colors.primaryBlue,
    padding: spacing.lg,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.white,
  },
  totalAmount: {
    fontSize: 28,
    fontWeight: '900',
    color: colors.white,
  },
  actions: {
    padding: spacing.lg,
    gap: spacing.md,
    marginBottom: spacing.xl,
  },
  primaryButton: {
    backgroundColor: colors.actionOrange,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    alignItems: 'center',
  },
  primaryButtonText: {
    color: colors.white,
    fontSize: 16,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  secondaryButton: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
    gap: spacing.sm,
    borderWidth: 2,
    borderColor: colors.primaryBlue,
  },
  secondaryButtonText: {
    color: colors.primaryBlue,
    fontSize: 16,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
});

export default EstimateScreen;
