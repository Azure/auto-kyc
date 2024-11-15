// src/pages/UploadDocuments.js
import React, { useContext, useEffect } from 'react';
import axios from 'axios';
import { GlobalStateContext } from '../GlobalState';
import {
  Typography,
  Button,
  Input,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Card,
  CardMedia,
} from '@mui/material';

const apiBaseUrl = window.API_BASE_URL;

function UploadDocuments() {
  const {
    uploadedFiles,
    setUploadedFiles,
    selectedImageIndex,
    setSelectedImageIndex,
  } = useContext(GlobalStateContext);

  // List of default documents with paths to sample images
  const defaultDocuments = [
    { name: 'sample-id1.jpg', url: '/sample-documents/sample-id1.jpg' },
    { name: 'sample-id2.jpg', url: '/sample-documents/sample-id2.jpg' },
    { name: 'sample-id3.jpg', url: '/sample-documents/sample-id3.jpg' },
    { name: 'sample-id4.jpg', url: '/sample-documents/sample-id4.jpg' },
  ];

  // Load default documents when the component mounts
  useEffect(() => {
    const loadDefaultDocuments = async () => {
      const defaultFiles = await Promise.all(
        defaultDocuments.map(async (doc) => {
          const response = await fetch(doc.url);
          const blob = await response.blob();
          const fileReader = new FileReader();
          return new Promise((resolve) => {
            fileReader.onload = () => {
              resolve({ name: doc.name, dataUrl: fileReader.result });
            };
            fileReader.readAsDataURL(blob);
          });
        })
      );

      // Set uploaded files with default documents if not already set
      setUploadedFiles((prevFiles) => (prevFiles.length === 0 ? defaultFiles : prevFiles));
    };

    loadDefaultDocuments();
  }, [setUploadedFiles]);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    processFiles(files);
  };

  const processFiles = (filesArray) => {
    const filePromises = filesArray.map((file) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          resolve({ name: file.name, dataUrl: reader.result });
        };
        reader.onerror = (error) => reject(error);
        reader.readAsDataURL(file);
      });
    });

    Promise.all(filePromises)
      .then((fileDataArray) => {
        setUploadedFiles((prevFiles) => [...prevFiles, ...fileDataArray]);
      })
      .catch((error) => {
        console.error(error);
      });
  };

  const handleUpload = async () => {
    if (uploadedFiles.length === 0) {
      alert('Please select files to upload.');
      return;
    }

    const formData = new FormData();
    for (const fileData of uploadedFiles) {
      const blob = dataURLToBlob(fileData.dataUrl);
      formData.append('files', blob, fileData.name);
    }

    try {
      await axios.post(`${apiBaseUrl}/api/upload`, formData);
      alert('Files uploaded successfully.');
    } catch (error) {
      console.error(error);
      alert('File upload failed.');
    }
  };

  const dataURLToBlob = (dataUrl) => {
    const arr = dataUrl.split(',');
    const mimeMatch = arr[0].match(/:(.*?);/);
    const mime = mimeMatch ? mimeMatch[1] : '';
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);

    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }

    return new Blob([u8arr], { type: mime });
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        Upload ID Documents
      </Typography>

      <Input type="file" inputProps={{ multiple: true }} onChange={handleFileChange} />
      {uploadedFiles.length > 0 && (
        <Box mt={2}>
          <Button variant="contained" color="primary" onClick={handleUpload}>
            Upload Files
          </Button>
        </Box>
      )}
      {uploadedFiles.length > 0 && (
        <>
          <Typography variant="h5" gutterBottom style={{ marginTop: '20px' }}>
            Document Viewer
          </Typography>
          <FormControl fullWidth>
            <InputLabel>Select an image to view</InputLabel>
            <Select
              value={selectedImageIndex < uploadedFiles.length ? selectedImageIndex : 0}
              onChange={(e) => setSelectedImageIndex(e.target.value)}
            >
              {uploadedFiles.map((file, index) => (
                <MenuItem key={index} value={index}>
                  {file.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Box mt={2} sx={{ padding: 2 }}>
            <Card>
              <CardMedia
                component="img"
                image={
                  uploadedFiles[selectedImageIndex] &&
                  uploadedFiles[selectedImageIndex].dataUrl
                    ? uploadedFiles[selectedImageIndex].dataUrl
                    : '' // Fallback in case dataUrl is undefined
                }
                alt={
                  uploadedFiles[selectedImageIndex]
                    ? uploadedFiles[selectedImageIndex].name
                    : 'No image selected'
                }
                sx={{
                  maxWidth: '100%',
                  maxHeight: '500px',
                  objectFit: 'contain',
                }}
              />
            </Card>
          </Box>
        </>
      )}
    </div>
  );
}

export default UploadDocuments;
