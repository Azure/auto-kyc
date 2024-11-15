// src/pages/ViewEditCustomerData.js
import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { GlobalStateContext } from '../GlobalState';
import {
  Typography,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Box,
} from '@mui/material';

const apiBaseUrl = window.API_BASE_URL;
console.log('API base URL:', apiBaseUrl);

function ViewEditCustomerData() {
  const {
    customerList,
    setCustomerList,
    selectedCustomerId,
    setSelectedCustomerId,
    customerData,
    setCustomerData,
  } = useContext(GlobalStateContext);
  const [customerDataText, setCustomerDataText] = useState('');

  useEffect(() => {
    fetchCustomerList();
  }, []);

  useEffect(() => {
    if (customerData && Object.keys(customerData).length > 0) {
      setCustomerDataText(JSON.stringify(customerData, null, 2));
    }
  }, [customerData]);

  const fetchCustomerList = async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/api/customers`);
      console.log('Customer list response:', response.data);
      setCustomerList(response.data);
    } catch (error) {
      console.error(error);
      alert('Failed to fetch customer list.');
    }
  };

  const handleCustomerSelect = (e) => {
    setSelectedCustomerId(e.target.value);
  };

  const handleLoadCustomer = async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/api/customer/${selectedCustomerId}`);
      setCustomerData(response.data);
      setCustomerDataText(JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.error(error);
      alert('Customer not found.');
    }
  };

  const handleCustomerDataChange = (e) => {
    setCustomerDataText(e.target.value);
  };

  const handleUpdateDB = async () => {
    try {
      const data = JSON.parse(customerDataText);
      await axios.post(`${apiBaseUrl}/api/update`, data);
      alert('Database updated successfully.');
      setCustomerData(data); // Update the global state
    } catch (error) {
      console.error(error);
      alert('Failed to update database.');
    }
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        View and Edit Customer Records
      </Typography>
      <Typography variant="h6">Select a Customer</Typography>
      <FormControl fullWidth>
        <InputLabel>Select a customer</InputLabel>
        <Select value={selectedCustomerId} onChange={handleCustomerSelect}>
          {customerList.map((cust) => (
            <MenuItem key={cust.id} value={cust.id}>
              {cust.id} - {cust.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <Box mt={2}>
        <Button variant="contained" color="primary" onClick={handleLoadCustomer}>
          Load Selected Customer
        </Button>
      </Box>
      {customerDataText && (
        <>
          <Typography variant="h6" style={{ marginTop: '20px' }}>
            Customer Data (Editable)
          </Typography>
          <TextField
            label="Edit Customer Data"
            value={customerDataText}
            onChange={handleCustomerDataChange}
            multiline
            rows={15}
            fullWidth
            variant="outlined"
          />
          <Box mt={2}>
            <Button variant="contained" color="secondary" onClick={handleUpdateDB}>
              Update DB
            </Button>
          </Box>
        </>
      )}
    </div>
  );
}

export default ViewEditCustomerData;
