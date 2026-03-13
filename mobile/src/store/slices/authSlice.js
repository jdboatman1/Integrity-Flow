import {createSlice, createAsyncThunk} from '@reduxjs/toolkit';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {erpnextAPI} from '../../api/erpnext';

export const login = createAsyncThunk(
  'auth/login',
  async ({username, password}) => {
    const response = await erpnextAPI.login(username, password);
    // Store credentials
    await AsyncStorage.multiSet([
      ['api_key', response.api_key],
      ['api_secret', response.api_secret],
      ['user_data', JSON.stringify(response.user)],
    ]);
    return response;
  },
);

export const logout = createAsyncThunk('auth/logout', async () => {
  await AsyncStorage.multiRemove(['api_key', 'api_secret', 'user_data']);
});

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null,
  },
  reducers: {
    setUser: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    clearUser: state => {
      state.user = null;
      state.isAuthenticated = false;
    },
  },
  extraReducers: builder => {
    builder
      .addCase(login.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(logout.fulfilled, state => {
        state.user = null;
        state.isAuthenticated = false;
      });
  },
});

export const {setUser, clearUser} = authSlice.actions;
export default authSlice.reducer;
