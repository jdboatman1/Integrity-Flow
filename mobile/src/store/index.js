import {configureStore} from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import estimateReducer from './slices/estimateSlice';
import customerReducer from './slices/customerSlice';
import offlineReducer from './slices/offlineSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    estimate: estimateReducer,
    customer: customerReducer,
    offline: offlineReducer,
  },
});
