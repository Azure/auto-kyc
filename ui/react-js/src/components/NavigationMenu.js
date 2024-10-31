// src/components/NavigationMenu.js
import React, { useContext } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemText,
  Toolbar,
  Divider,
  Box,
  Typography,
  Alert,
} from '@mui/material';
import { GlobalStateContext } from '../GlobalState';

function NavigationMenu({ handleNavigation }) {
  const { status, photoStatus, logs } = useContext(GlobalStateContext);

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: 340, // Fixed width for the sidebar
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: 340,
          boxSizing: 'border-box',
        },
        display: { xs: 'none', sm: 'block' }, // Hide on extra-small screens
      }}
    >
      <Toolbar />
      <Divider />
      <List>
        <ListItem button onClick={() => handleNavigation('home')}>
          <ListItemText primary="Home" />
        </ListItem>
        <ListItem button onClick={() => handleNavigation('upload-documents')}>
          <ListItemText primary="Upload Documents" />
        </ListItem>
        <ListItem button onClick={() => handleNavigation('view-edit-customer-data')}>
          <ListItemText primary="View/Edit Customer Data" />
        </ListItem>
        <ListItem button onClick={() => handleNavigation('document-comparison')}>
          <ListItemText primary="Document Comparison" />
        </ListItem>
        {/* New Liveness Check Navigation Item */}
        <ListItem button onClick={() => handleNavigation('liveness-check')}>
          <ListItemText primary="Liveness Check" />
        </ListItem>
      </List>
      <Divider />
      <Box
        sx={{
          padding: 2,
          overflowY: 'auto', // Make the content scrollable if it exceeds the sidebar height
          height: 'calc(100% - 64px)', // Adjust height to ensure scroll area fits within the fixed width
        }}
      >
        <Typography variant="h6">Status Indicator</Typography>
        {status && (
          <Alert severity={status === 'OK' ? 'success' : 'error'}>Data Status: {status}</Alert>
        )}
        {photoStatus && (
          <Alert severity={photoStatus === 'OK' ? 'success' : 'error'}>
            Photo Status: {photoStatus}
          </Alert>
        )}
        <Typography variant="h6" sx={{ marginTop: 2 }}>
          Log Viewer
        </Typography>
        {logs && logs.length > 0 ? (
          logs.map((log, index) => (
            <Alert key={index} severity={log.type || 'info'}>
              {log.message}
            </Alert>
          ))
        ) : (
          <Alert severity="info">No logs available.</Alert>
        )}
      </Box>
    </Drawer>
  );
}

export default NavigationMenu;
