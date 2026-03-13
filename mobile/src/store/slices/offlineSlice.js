import {createSlice} from '@reduxjs/toolkit';

const offlineSlice = createSlice({
  name: 'offline',
  initialState: {
    pendingEstimates: [],
    pendingPhotos: [],
    isOnline: true,
  },
  reducers: {
    setOnlineStatus: (state, action) => {
      state.isOnline = action.payload;
    },
    addPendingEstimate: (state, action) => {
      state.pendingEstimates.push(action.payload);
    },
    removePendingEstimate: (state, action) => {
      state.pendingEstimates = state.pendingEstimates.filter(
        item => item.id !== action.payload,
      );
    },
    addPendingPhoto: (state, action) => {
      state.pendingPhotos.push(action.payload);
    },
    removePendingPhoto: (state, action) => {
      state.pendingPhotos = state.pendingPhotos.filter(
        item => item.id !== action.payload,
      );
    },
  },
});

export const {
  setOnlineStatus,
  addPendingEstimate,
  removePendingEstimate,
  addPendingPhoto,
  removePendingPhoto,
} = offlineSlice.actions;
export default offlineSlice.reducer;
