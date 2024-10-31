// src/pages/HomePage.js
import React from 'react';
import { Typography } from '@mui/material';

function HomePage() {
  return (
    <div>
      <Typography variant="h4" gutterBottom>
        Welcome to the Know Your Customer (KYC) Application
      </Typography>
      <Typography variant="body1">
        Please select a page from the navigation menu to proceed.
      </Typography>
    </div>
  );
}

export default HomePage;
