// src/App.js
import React, { useState } from 'react';
import { GlobalStateProvider } from './GlobalState';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import {
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  useMediaQuery,
} from '@mui/material';
import HomePage from './pages/HomePage';
import UploadDocuments from './pages/UploadDocuments';
import ViewEditCustomerData from './pages/ViewEditCustomerData';
import DocumentComparison from './pages/DocumentComparison';
import LivenessCheck from './pages/LivenessCheck'; // Import the new Liveness Check component
import NavigationMenu from './components/NavigationMenu';

const theme = createTheme();

function App() {
  const [currentView, setCurrentView] = useState('home');

  // Function to change the current view
  const handleNavigation = (view) => {
    setCurrentView(view);
  };

  // Render the component based on the current view
  const renderView = () => {
    switch (currentView) {
      case 'upload-documents':
        return <UploadDocuments />;
      case 'view-edit-customer-data':
        return <ViewEditCustomerData />;
      case 'document-comparison':
        return <DocumentComparison />;
      case 'liveness-check': // Add a case for the Liveness Check
        return <LivenessCheck />;
      default:
        return <HomePage />;
    }
  };

  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <GlobalStateProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ display: 'flex', flexDirection: 'row' }}>
          <AppBar position="fixed">
            <Toolbar>
              <Typography variant="h6">KYC Application</Typography>
            </Toolbar>
          </AppBar>
          <NavigationMenu handleNavigation={handleNavigation} />
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              marginTop: '80px',
              marginLeft: '0px',
              paddingLeft: '16px',
              paddingRight: '16px',
              overflowX: 'hidden',
            }}
          >
            {renderView()}
          </Box>
        </Box>
      </ThemeProvider>
    </GlobalStateProvider>
  );
}

export default App;
