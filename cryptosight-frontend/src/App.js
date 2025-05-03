// src/App.js
import React from 'react';
import { ThemeProvider, createTheme, CssBaseline,Typography, Box, Container } from '@mui/material';
import Header from './components/Header';
import ChatInterface from './components/ChatInterface';


// Create a custom theme with our primary color
const theme = createTheme({
  palette: {
    primary: {
      main: '#f7b84b',
    },
    secondary: {
      main: '#4caf50',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

// In your App.js file

function App() {
  return (
    <Box sx={{ 
      minHeight: '100vh', 
      backgroundColor: '#fffff',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Floating header with shadow */}
      <Box sx={{ p: 2, mb: 2 }}>
        <Box 
          sx={{ 
            backgroundColor: 'white',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)',
            borderRadius: 2,
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            maxWidth: '1200px',
            margin: '0 auto',
            position: 'relative',
            zIndex: 10
          }}
        >
          <Typography 
            variant="h5" 
            component="h1" 
            sx={{ 
              fontWeight: 700, 
              fontFamily: 'monospace',
              color: '#333',
              fontSize: '1.5rem'
            }}
          >
            Scova
          </Typography>
          
          {/* You can add additional header elements here if needed */}
        </Box>
      </Box>
      
      {/* Main content */}
      <Box sx={{ flex: 1 }}>
        <Container maxWidth="md" 
          sx={{ 
            maxWidth: '1050px !important', // A width between md and lg
            mb: 4,
            px: 2
          }}>
          <ChatInterface />
        </Container>
      </Box>
    </Box>
  );
}

export default App;