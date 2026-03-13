import {createSlice, createAsyncThunk} from '@reduxjs/toolkit';
import {erpnextAPI} from '../../api/erpnext';
import {storeOffline} from '../../utils/offline';

export const createEstimate = createAsyncThunk(
  'estimate/create',
  async (estimateData, {rejectWithValue}) => {
    try {
      const response = await erpnextAPI.createQuotation(estimateData);
      return response;
    } catch (error) {
      // Store offline if no connection
      await storeOffline('estimate', estimateData);
      return rejectWithValue('Stored offline - will sync when online');
    }
  },
);

export const fetchEstimates = createAsyncThunk(
  'estimate/fetchAll',
  async () => {
    const response = await erpnextAPI.getQuotations();
    return response;
  },
);

const estimateSlice = createSlice({
  name: 'estimate',
  initialState: {
    estimates: [],
    currentEstimate: null,
    loading: false,
    error: null,
  },
  reducers: {
    setCurrentEstimate: (state, action) => {
      state.currentEstimate = action.payload;
    },
    clearCurrentEstimate: state => {
      state.currentEstimate = null;
    },
    addLineItem: (state, action) => {
      if (!state.currentEstimate) {
        state.currentEstimate = {items: []};
      }
      if (!state.currentEstimate.items) {
        state.currentEstimate.items = [];
      }
      state.currentEstimate.items.push(action.payload);
    },
    removeLineItem: (state, action) => {
      if (state.currentEstimate?.items) {
        state.currentEstimate.items = state.currentEstimate.items.filter(
          (_, index) => index !== action.payload,
        );
      }
    },
  },
  extraReducers: builder => {
    builder
      .addCase(createEstimate.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createEstimate.fulfilled, (state, action) => {
        state.loading = false;
        state.estimates.push(action.payload);
        state.currentEstimate = null;
      })
      .addCase(createEstimate.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchEstimates.fulfilled, (state, action) => {
        state.estimates = action.payload;
      });
  },
});

export const {
  setCurrentEstimate,
  clearCurrentEstimate,
  addLineItem,
  removeLineItem,
} = estimateSlice.actions;
export default estimateSlice.reducer;
