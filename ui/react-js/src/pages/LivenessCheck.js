// src/pages/LivenessCheck.js
import React, { useState, useEffect, useContext } from 'react';
import {
  Typography,
  Box,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Card,
  CardMedia,
} from '@mui/material';
import { GlobalStateContext } from '../GlobalState';

function LivenessCheck() {
  const [authToken, setAuthToken] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [cameras, setCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState('');
  const { customerData, setCustomerData } = useContext(GlobalStateContext);

  useEffect(() => {
    import('azure-ai-vision-face-ui')
      .then(() => {
        console.log('azure-ai-vision-face-ui component loaded successfully.');
        getAvailableCameras();
      })
      .catch((error) => {
        console.error('Failed to load azure-ai-vision-face-ui component:', error);
      });
  }, []);

  useEffect(() => {
    if (customerData && customerData.photo) {
      handleLoadCustomerPhoto();
    }
  }, []); // Run when component mounts

  const getAvailableCameras = async () => {
    try {
      // Request camera access first
      await navigator.mediaDevices.getUserMedia({ video: true });
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter((device) => device.kind === 'videoinput');
      setCameras(videoDevices);
      if (videoDevices.length > 0) {
        setSelectedCamera(videoDevices[0].deviceId);
      } else {
        console.warn('No video input devices found.');
      }
    } catch (error) {
      console.error('Error accessing camera devices:', error);
    }
  };

  const handleLoadCustomerPhoto = async () => {
    try {
      if (customerData.photo) {
        const photoUrl = customerData.photo.replace(/['"]/g, '');
        const response = await fetch('http://localhost:80/api/get_sas', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: photoUrl }),
        });
        const sasData = await response.json();
        const updatedCustomerData = { ...customerData, photo_sas: sasData.sas };
        setCustomerData(updatedCustomerData);
      }
    } catch (error) {
      console.error(error);
      alert('Failed to load customer photo.');
    }
  };

  const createLivenessSession = async () => {
    try {
      // Ensure customer photo is available
      if (!customerData.photo_sas) {
        alert('Customer photo not available. Please select a customer with a photo.');
        return;
      }

      // Fetch the customer photo
      const response = await fetch(customerData.photo_sas);
      const blob = await response.blob();
      const file = new File([blob], 'verify_image.jpg', { type: blob.type });

      // Create the session request parameters
      const sessionRequest = {
        livenessOperationMode: 'Passive',
        sendResultsToClient: true,
        deviceCorrelationId: getDummyDeviceId(),
      };

      // Create FormData and append parameters and image
      const formData = new FormData();
      formData.append('parameters', JSON.stringify(sessionRequest));
      formData.append('verify_image', file);

      // Send the request to the backend
      const sessionResponse = await fetch('http://localhost:80/api/detectLiveness', {
        method: 'POST',
        body: formData,
      });

      const session = await sessionResponse.json();
      console.log('Session created:', session);

      if (!session || !session.authToken || !session.session_id) {
        throw new Error('Failed to create session');
      }

      setAuthToken(session.authToken);
      setSessionId(session.session_id);
      setFeedbackMessage('Starting liveness check...');

      initializeFaceLiveness(session.authToken);
    } catch (error) {
      console.error('Session creation failed:', error);
      setFeedbackMessage(`Error: ${error.message}`);
    }
  };

  const initializeFaceLiveness = (token) => {
    const livenessContainer = document.getElementById('livenessContainer');

    if (!livenessContainer) {
      console.error('Liveness container not found.');
      setFeedbackMessage('Error: Liveness container not found.');
      return;
    }

    livenessContainer.innerHTML = '';

    const azureAIVisionFaceUI = document.createElement('azure-ai-vision-face-ui');
    azureAIVisionFaceUI.assetPath = '/facelivenessdetector-assets/js';
    azureAIVisionFaceUI.mediaInfoDeviceId = selectedCamera;

    // Custom language dictionary (optional)
    azureAIVisionFaceUI.languageDictionary = {
      "None": "Please hold still.",
      "LookAtCamera": "Look at the camera.",
      "FaceNotCentered": "Center your face in the circle.",
      "MoveCloser": "Please move closer.",
      "TooMuchMovement": "Too much movement detected.",
      "TimedOut": "Session timed out.",
      "IncreaseBrightnessToMax": "Increase screen brightness to maximum.",
      "Smile": "Smile for the camera!",
      "LookInFront": "Look straight ahead.",
      "Continue": "Continue",
      "HoldStill": "Hold still.",
      "FaceDetected": "Face detected.",
      "NoFaceDetected": "No face detected.",
      "Processing": "Processing...",
      "Authenticating": "Authenticating...",
      "LivenessComplete": "Liveness check complete.",
      "RealFaceDetected": "Real face detected.",
      "SpoofFaceDetected": "Spoof face detected.",
      "Tip1Title": "Tip 1:", 
      "Tip1": "Center your face in the preview.",
      "Tip2Title": "Tip 2:", 
      "Tip2": "You may be asked to smile.",
      "Tip3Title": "Tip 3:", 
      "Tip3": "You may be asked to move your nose towards the green color.",
      "AttentionNotNeeded": "Ok, you can relax now.",
      "ContinueToMoveCloser": "Please move closer to the camera.",
    };

    livenessContainer.appendChild(azureAIVisionFaceUI);

    azureAIVisionFaceUI
      .start(token)
      .then((resultData) => {
        handleLivenessResult(resultData);
      })
      .catch((errorData) => {
        handleLivenessError(errorData);
      });
  };

  const handleLivenessResult = (resultData) => {
    let message = `Liveness Status: ${resultData.livenessStatus}`;
    if (resultData.recognitionResult && resultData.recognitionResult.status) {
      message += `\nVerification Status: ${resultData.recognitionResult.status}`;
    }
    setFeedbackMessage(message);
    notifyServerLivenessCompletion(resultData);
  };

  const handleLivenessError = (errorData) => {
    setFeedbackMessage(`Error: ${errorData.livenessError || errorData.message}`);
  };

  const notifyServerLivenessCompletion = async (resultData) => {
    try {
      await fetch('http://localhost:80/api/livenessComplete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          result: resultData,
        }),
      });
      console.log('Liveness completion notified to server');
    } catch (error) {
      console.error('Failed to notify server of liveness completion:', error);
    }
  };

  const getDummyDeviceId = () => {
    const length = 10;
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    return Array.from({ length }, () =>
      characters.charAt(Math.floor(Math.random() * characters.length))
    ).join('');
  };

  return (
    <Box sx={{ padding: 2, textAlign: 'center', maxWidth: '500px', margin: '0 auto' }}>
      <Typography variant="h4" gutterBottom>
        Liveness Check
      </Typography>

      {customerData.photo_sas && (
        <Box sx={{ marginTop: 2 }}>
          <Typography variant="h6">Reference Photo</Typography>
          <Card sx={{ maxWidth: 300, margin: '0 auto' }}>
            <CardMedia component="img" image={customerData.photo_sas} alt="Customer Photo" />
          </Card>
        </Box>
      )}

      <FormControl fullWidth sx={{ marginTop: 2, marginBottom: 3 }}>
        <InputLabel>Select Camera</InputLabel>
        <Select
          value={selectedCamera}
          onChange={(e) => setSelectedCamera(e.target.value)}
          label="Select Camera"
        >
          {cameras.map((camera, index) => (
            <MenuItem key={index} value={camera.deviceId}>
              {camera.label || `Camera ${index + 1}`}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Button
        variant="contained"
        color="primary"
        onClick={createLivenessSession}
        fullWidth
        sx={{ marginBottom: 4 }}
        disabled={!customerData.photo_sas}
      >
        Start Liveness Check
      </Button>

      {feedbackMessage && (
        <Typography
          variant="h5"
          color="textPrimary"
          fontWeight="bold"
          sx={{ marginTop: 4, whiteSpace: 'pre-line' }}
        >
          {feedbackMessage}
        </Typography>
      )}

      <div id="livenessContainer" style={{ width: '100%', height: '400px', marginTop: 2 }}></div>
    </Box>
  );
}

export default LivenessCheck;
