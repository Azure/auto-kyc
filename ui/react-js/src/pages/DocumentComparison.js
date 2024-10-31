// src/pages/DocumentComparison.js
import React, { useEffect, useContext, useState } from 'react';
import axios from 'axios';
import { GlobalStateContext } from '../GlobalState';
import {
  Typography,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Card,
  CardMedia,
  Grid,
  Alert,
  CircularProgress,
  Switch,
} from '@mui/material';

function DocumentComparison() {
  const {
    uploadedFiles,
    setUploadedFiles,
    selectedImageIndex,
    setSelectedImageIndex,
    customerData,
    setCustomerData,
    extractedData,
    setExtractedData,
    logs,
    setLogs,
    status,
    setStatus,
    photoStatus,
    setPhotoStatus,
  } = useContext(GlobalStateContext);

  const [loading, setLoading] = useState(false);
  const [showProcessedIdDocument, setShowProcessedIdDocument] = useState(false);
  const [showProcessedCustomerPhoto, setShowProcessedCustomerPhoto] = useState(false);

  // Function to filter customer data by excluding specific keys
  const getFilteredCustomerData = () => {
    return Object.fromEntries(
      Object.entries(customerData).filter(
        ([key]) => !key.startsWith('_') && key !== 'photo_sas' && key !== 'processedPhotoUrl'
      )
    );
  };

  const handleSelectImage = (e) => {
    setSelectedImageIndex(e.target.value);
  };

  // Load customer photo if not already loaded
  useEffect(() => {
    if (customerData && customerData.id && !customerData.photo_sas && customerData.photo) {
      handleLoadCustomerPhoto();
    }
  }, [customerData]);

  const handleLoadCustomerPhoto = async () => {
    try {
      if (customerData.photo) {
        const photoUrl = customerData.photo.replace(/['"]/g, '');
        const sasResponse = await axios.post('http://localhost:80/api/get_sas', {
          url: photoUrl,
        });
        const updatedCustomerData = { ...customerData, photo_sas: sasResponse.data.sas };
        setCustomerData(updatedCustomerData);
      }
    } catch (error) {
      console.error(error);
      alert('Failed to load customer photo.');
    }
  };

  const handleAnalyzeDocuments = async () => {
    if (!customerData || !customerData.id || !uploadedFiles[selectedImageIndex]) {
      alert('Please select a customer in "View/Edit Customer Data" and upload documents.');
      return;
    }

    try {
      setLoading(true);
      const fileData = uploadedFiles[selectedImageIndex];
      const base64data = fileData.dataUrl.split(',')[1];
      const info = {
        customer_id: customerData.id,
        id_document: base64data,
        id_document_name: fileData.name,
      };
      const response = await axios.post('http://localhost:80/api/analyze', info);

      // Update extracted data and logs
      setExtractedData(response.data.document_id_extracted_data);
      setLogs(response.data.log_checks);
      setStatus(response.data.data_fields_status ? 'OK' : 'Not OK');
      setPhotoStatus(response.data.photo_comparison_status ? 'OK' : 'Not OK');

      // Extract the processed image URLs
      const photoComparisonResult = response.data.photo_comparison_result;
      const processedIdDocumentUrl = photoComparisonResult.photo_1;
      const processedCustomerPhotoUrl = photoComparisonResult.photo_2;

      // Get SAS URLs for the processed images
      const processedIdDocumentSasResponse = await axios.post('http://localhost:80/api/get_sas', {
        url: processedIdDocumentUrl,
      });
      const processedCustomerPhotoSasResponse = await axios.post('http://localhost:80/api/get_sas', {
        url: processedCustomerPhotoUrl,
      });

      // Update the uploadedFiles with the processed image SAS URL
      const updatedFiles = [...uploadedFiles];
      updatedFiles[selectedImageIndex] = {
        ...fileData,
        processedDataUrl: processedIdDocumentSasResponse.data.sas,
      };
      setUploadedFiles(updatedFiles);

      // Update customerData with processed photo SAS URL
      const updatedCustomerData = {
        ...customerData,
        processedPhotoUrl: processedCustomerPhotoSasResponse.data.sas,
      };
      setCustomerData(updatedCustomerData);

      // Automatically turn on the toggles for processed images
      setShowProcessedIdDocument(true);
      setShowProcessedCustomerPhoto(true);
    } catch (error) {
      console.error(error);
      alert('Analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        Document Comparison
      </Typography>
      {customerData && customerData.id ? (
        <>
          <Grid container spacing={4}>
            {/* Left Column */}
            <Grid item xs={12} md={6} style={{ textAlign: 'center' }}>
              <Typography variant="h6">Customer Information</Typography>
              <Typography variant="body1">
                Full Name: {customerData.first_name} {customerData.middle_name}{' '}
                {customerData.last_name}
              </Typography>
              {customerData.photo_sas && (
                <Box mt={2} display="flex" flexDirection="column" alignItems="center">
                  {/* Toggle Button */}
                  <Box display="flex" alignItems="center" sx={{ marginBottom: 1 }}>
                    <Typography variant="body1" sx={{ marginRight: 1 }}>
                      Original
                    </Typography>
                    <Switch
                      checked={showProcessedCustomerPhoto}
                      onChange={(e) => setShowProcessedCustomerPhoto(e.target.checked)}
                      color="primary"
                    />
                    <Typography variant="body1">Analyzed</Typography>
                  </Box>
                  <Card sx={{ maxWidth: 180 }}>
                    <CardMedia
                      component="img"
                      image={
                        showProcessedCustomerPhoto && customerData.processedPhotoUrl
                          ? customerData.processedPhotoUrl
                          : customerData.photo_sas
                      }
                      alt="Customer Photo"
                    />
                  </Card>
                </Box>
              )}
            </Grid>
            {/* Right Column */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6">Document Viewer</Typography>
              {uploadedFiles.length > 0 ? (
                <>
                  <FormControl fullWidth>
                    <InputLabel>Select a document to view</InputLabel>
                    <Select value={selectedImageIndex} onChange={handleSelectImage}>
                      {uploadedFiles.map((file, index) => (
                        <MenuItem key={index} value={index}>
                          {file.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <Box mt={2} sx={{ padding: 2 }}>
                    {/* Toggle Button */}
                    <Box display="flex" alignItems="center">
                      <Typography variant="body1" sx={{ marginRight: 1 }}>
                        Original
                      </Typography>
                      <Switch
                        checked={showProcessedIdDocument}
                        onChange={(e) => setShowProcessedIdDocument(e.target.checked)}
                        color="primary"
                      />
                      <Typography variant="body1">Analyzed</Typography>
                    </Box>
                    <Card>
                      <CardMedia
                        component="img"
                        image={
                          showProcessedIdDocument && uploadedFiles[selectedImageIndex].processedDataUrl
                            ? uploadedFiles[selectedImageIndex].processedDataUrl
                            : uploadedFiles[selectedImageIndex].dataUrl
                        }
                        alt={uploadedFiles[selectedImageIndex].name}
                        sx={{
                          maxWidth: '100%',
                          maxHeight: '500px',
                          objectFit: 'contain',
                        }}
                      />
                    </Card>
                  </Box>
                </>
              ) : (
                <Alert severity="info" style={{ marginTop: '20px' }}>
                  No documents uploaded. Please upload documents in the 'Upload Documents' page.
                </Alert>
              )}
            </Grid>
          </Grid>
          <Box mt={4} display="flex" flexDirection="column" alignItems="center">
            <Button
              variant="contained"
              color="secondary"
              onClick={handleAnalyzeDocuments}
              disabled={loading || !uploadedFiles.length}
            >
              Analyze Documents
            </Button>
            {loading && (
              <Box mt={2}>
                <CircularProgress />
                <Typography variant="body2" style={{ marginTop: '10px' }}>
                  Analyzing documents, please wait...
                </Typography>
              </Box>
            )}
          </Box>
          <Grid container spacing={4} style={{ marginTop: '20px' }}>
            {/* Left Column */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6">Stored Data</Typography>
              <pre
                style={{
                  backgroundColor: '#f5f5f5',
                  padding: '10px',
                  whiteSpace: 'pre-wrap',
                  wordWrap: 'break-word',
                }}
              >
                {JSON.stringify(getFilteredCustomerData(), null, 2)}
              </pre>
            </Grid>
            {/* Right Column */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6">Extracted Data</Typography>
              <pre
                style={{
                  backgroundColor: '#f5f5f5',
                  padding: '10px',
                  whiteSpace: 'pre-wrap',
                  wordWrap: 'break-word',
                }}
              >
                {JSON.stringify(extractedData, null, 2)}
              </pre>
            </Grid>
          </Grid>
        </>
      ) : (
        <Alert severity="info">
          No customer selected. Please select a customer in the 'View/Edit Customer Data' page.
        </Alert>
      )}
    </div>
  );
}

export default DocumentComparison;
