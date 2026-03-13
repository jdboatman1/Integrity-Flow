import React, {useState} from 'react';
import {
  View,
  TouchableOpacity,
  Image,
  StyleSheet,
  Alert,
} from 'react-native';
import {launchCamera, launchImageLibrary} from 'react-native-image-picker';
import Icon from 'react-native-vector-icons/Ionicons';
import {colors, spacing, borderRadius} from '../theme';
import {erpnextAPI} from '../api/erpnext';

const PhotoCapture = ({estimateId, onPhotoAdded}) => {
  const [photos, setPhotos] = useState([]);
  const [uploading, setUploading] = useState(false);

  const handleTakePhoto = async () => {
    const result = await launchCamera({
      mediaType: 'photo',
      quality: 0.8,
      saveToPhotos: true,
    });

    if (result.assets && result.assets.length > 0) {
      const photo = result.assets[0];
      await uploadPhoto(photo);
    }
  };

  const handleChoosePhoto = async () => {
    const result = await launchImageLibrary({
      mediaType: 'photo',
      quality: 0.8,
      selectionLimit: 1,
    });

    if (result.assets && result.assets.length > 0) {
      const photo = result.assets[0];
      await uploadPhoto(photo);
    }
  };

  const uploadPhoto = async photo => {
    if (!estimateId) {
      Alert.alert('Error', 'Please save the estimate first');
      return;
    }

    setUploading(true);
    try {
      const response = await erpnextAPI.uploadFile(
        photo,
        'Quotation',
        estimateId,
      );
      setPhotos([...photos, response]);
      if (onPhotoAdded) {
        onPhotoAdded(response);
      }
      Alert.alert('Success', 'Photo uploaded successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to upload photo');
    } finally {
      setUploading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.buttons}>
        <TouchableOpacity
          style={styles.button}
          onPress={handleTakePhoto}
          disabled={uploading}
          testID="take-photo-button">
          <Icon name="camera" size={24} color={colors.white} />
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.button}
          onPress={handleChoosePhoto}
          disabled={uploading}
          testID="choose-photo-button">
          <Icon name="images" size={24} color={colors.white} />
        </TouchableOpacity>
      </View>

      <View style={styles.photoGrid}>
        {photos.map((photo, index) => (
          <Image
            key={index}
            source={{uri: photo.file_url}}
            style={styles.photo}
          />
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: spacing.md,
  },
  buttons: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.md,
  },
  button: {
    flex: 1,
    backgroundColor: colors.primaryBlue,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  photoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  photo: {
    width: 100,
    height: 100,
    borderRadius: borderRadius.md,
  },
});

export default PhotoCapture;
