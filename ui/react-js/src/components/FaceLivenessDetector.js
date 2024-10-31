// src/components/FaceLivenessDetector.js
import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';

// Mock statuses to simulate the liveness check
const LivenessStatus = {
  RealFace: "RealFace",
  SpoofFace: "SpoofFace",
};

function FaceLivenessDetector({ authToken, onComplete, onError }) {
  const [status, setStatus] = useState("Idle");
  const videoRef = useRef(null); // Reference to the video element
  const streamRef = useRef(null); // Reference to the media stream

  useEffect(() => {
    // Initialize the camera as soon as the component mounts
    initializeCamera();

    // Clean up: Stop the video stream when the component unmounts
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []); // Empty dependency array to ensure it only runs once on mount

  useEffect(() => {
    if (authToken) {
      startLivenessCheck(authToken);
    }
  }, [authToken]);

  // Initialize the camera
  const initializeCamera = async () => {
    try {
      // Access the camera
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
      streamRef.current = stream;
    } catch (error) {
      console.error("Error accessing camera:", error);
      onError({ livenessError: "Camera access denied" });
    }
  };

  // Simulate the `startLivenessCheck` method as a Promise-based function
  const startLivenessCheck = (token) => {
    console.log("Liveness check started with token:", token);

    // Simulate a delay to mimic an asynchronous API call
    setTimeout(() => {
      // Randomly determine if liveness check is successful or a spoof
      const isRealFace = Math.random() > 0.2;

      if (isRealFace) {
        const resultData = { livenessStatus: LivenessStatus.RealFace };
        setStatus(resultData.livenessStatus);
        onComplete(resultData); // Call the success handler
      } else {
        const errorData = { livenessError: "Spoof detected" };
        setStatus(LivenessStatus.SpoofFace);
        onError(errorData); // Call the error handler
      }
    }, 2000); // Simulated delay (2 seconds)
  };

  return (
    <div className="face-liveness-detector">
      <p>Liveness Detector Status: {status}</p>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        style={{ width: '100%', maxHeight: '300px', backgroundColor: 'black' }}
      />
      <button onClick={() => startLivenessCheck(authToken)}>Start Liveness Check</button>
    </div>
  );
}

FaceLivenessDetector.propTypes = {
  authToken: PropTypes.string.isRequired,
  onComplete: PropTypes.func.isRequired,
  onError: PropTypes.func.isRequired,
};

export default FaceLivenessDetector;
