import {createSlice, createAsyncThunk} from '@reduxjs/toolkit';
import {erpnextAPI} from '../../api/erpnext';

export const fetchCustomers = createAsyncThunk(
  'customer/fetchAll',
  async () => {
    const response = await erpnextAPI.getCustomers();
    return response;
  },
);

export const fetchCustomer = createAsyncThunk(
  'customer/fetchOne',
  async customerId => {
    const response = await erpnextAPI.getCustomer(customerId);
    return response;
  },
);

const customerSlice = createSlice({
  name: 'customer',
  initialState: {
    customers: [],
    selectedCustomer: null,
    loading: false,
    error: null,
  },
  reducers: {
    setSelectedCustomer: (state, action) => {
      state.selectedCustomer = action.payload;
    },
    clearSelectedCustomer: state => {
      state.selectedCustomer = null;
    },
  },
  extraReducers: builder => {
    builder
      .addCase(fetchCustomers.pending, state => {
        state.loading = true;
      })
      .addCase(fetchCustomers.fulfilled, (state, action) => {
        state.loading = false;
        state.customers = action.payload;
      })
      .addCase(fetchCustomers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(fetchCustomer.fulfilled, (state, action) => {
        state.selectedCustomer = action.payload;
      });
  },
});

export const {setSelectedCustomer, clearSelectedCustomer} =
  customerSlice.actions;
export default customerSlice.reducer;
