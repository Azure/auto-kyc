// src/GlobalState.js
import React, { createContext, useState, useEffect } from 'react';

export const GlobalStateContext = createContext();

export const GlobalStateProvider = ({ children }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [customerData, setCustomerData] = useState({});
  const [customerList, setCustomerList] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [extractedData, setExtractedData] = useState({});
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState('');
  const [photoStatus, setPhotoStatus] = useState('');

  // Load state from localStorage when the application starts
  useEffect(() => {
    const storedFiles = JSON.parse(localStorage.getItem('uploadedFiles') || '[]');
    const storedImageIndex = parseInt(localStorage.getItem('selectedImageIndex'), 10) || 0;
    const storedSelectedCustomerId = localStorage.getItem('selectedCustomerId') || '';
    const storedExtractedData = JSON.parse(localStorage.getItem('extractedData') || '{}');
    const storedLogs = JSON.parse(localStorage.getItem('logs') || '[]');
    const storedStatus = localStorage.getItem('status') || '';
    const storedPhotoStatus = localStorage.getItem('photoStatus') || '';
    const storedCustomerData = JSON.parse(localStorage.getItem('customerData') || '{}');
    const storedCustomerList = JSON.parse(localStorage.getItem('customerList') || '[]');

    setUploadedFiles((prev) => (prev.length === 0 ? storedFiles : prev));
    setSelectedImageIndex((prev) => (prev === 0 ? storedImageIndex : prev));
    setSelectedCustomerId((prev) => (prev === '' ? storedSelectedCustomerId : prev));
    setExtractedData((prev) => (Object.keys(prev).length === 0 ? storedExtractedData : prev));
    setLogs((prev) => (prev.length === 0 ? storedLogs : prev));
    setStatus((prev) => (prev === '' ? storedStatus : prev));
    setPhotoStatus((prev) => (prev === '' ? storedPhotoStatus : prev));
    setCustomerData((prev) => (Object.keys(prev).length === 0 ? storedCustomerData : prev));
    setCustomerList((prev) => (prev.length === 0 ? storedCustomerList : prev));
  }, []);

  // Save state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('uploadedFiles', JSON.stringify(uploadedFiles));
    localStorage.setItem('selectedImageIndex', selectedImageIndex);
    localStorage.setItem('selectedCustomerId', selectedCustomerId);
    localStorage.setItem('extractedData', JSON.stringify(extractedData));
    localStorage.setItem('logs', JSON.stringify(logs));
    localStorage.setItem('status', status);
    localStorage.setItem('photoStatus', photoStatus);

    // Avoid storing photo_sas in localStorage, as it may expire
    const customerDataToSave = { ...customerData };
    delete customerDataToSave.photo_sas;
    localStorage.setItem('customerData', JSON.stringify(customerDataToSave));

    localStorage.setItem('customerList', JSON.stringify(customerList));
  }, [
    uploadedFiles,
    selectedImageIndex,
    selectedCustomerId,
    extractedData,
    logs,
    status,
    photoStatus,
    customerData,
    customerList,
  ]);

  return (
    <GlobalStateContext.Provider
      value={{
        uploadedFiles,
        setUploadedFiles,
        selectedImageIndex,
        setSelectedImageIndex,
        customerData,
        setCustomerData,
        customerList,
        setCustomerList,
        selectedCustomerId,
        setSelectedCustomerId,
        extractedData,
        setExtractedData,
        logs,
        setLogs,
        status,
        setStatus,
        photoStatus,
        setPhotoStatus,
      }}
    >
      {children}
    </GlobalStateContext.Provider>
  );
};
