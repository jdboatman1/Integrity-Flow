import React, {useRef, useState} from 'react';
import {View, StyleSheet, TouchableOpacity, Text, Alert} from 'react-native';
import SignatureCanvas from 'react-native-signature-canvas';
import {colors, spacing, borderRadius} from '../theme';

const SignatureScreen = ({navigation, route}) => {
  const signatureRef = useRef();
  const [signature, setSignature] = useState(null);

  const handleSignature = sig => {
    setSignature(sig);
    if (route.params?.onSignatureSaved) {
      route.params.onSignatureSaved(sig);
    }
    Alert.alert('Success', 'Signature captured!', [
      {text: 'OK', onPress: () => navigation.goBack()},
    ]);
  };

  const handleClear = () => {
    signatureRef.current?.clearSignature();
    setSignature(null);
  };

  return (
    <View style={styles.container}>
      <View style={styles.signatureContainer}>
        <SignatureCanvas
          ref={signatureRef}
          onOK={handleSignature}
          descriptionText="Sign above"
          clearText="Clear"
          confirmText="Save"
          webStyle={`.m-signature-pad { background-color: white; }`}
        />
      </View>
      <View style={styles.actions}>
        <TouchableOpacity style={styles.clearButton} onPress={handleClear}>
          <Text style={styles.clearButtonText}>Clear</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.gray100,
  },
  signatureContainer: {
    flex: 1,
    margin: spacing.lg,
    backgroundColor: colors.white,
    borderRadius: borderRadius.lg,
    overflow: 'hidden',
  },
  actions: {
    padding: spacing.lg,
  },
  clearButton: {
    backgroundColor: colors.gray600,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    alignItems: 'center',
  },
  clearButtonText: {
    color: colors.white,
    fontSize: 16,
    fontWeight: '700',
  },
});

export default SignatureScreen;
