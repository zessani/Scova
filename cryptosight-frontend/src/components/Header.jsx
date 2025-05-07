// src/components/Header.jsx
import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';

const Header = () => {
  return (
    <AppBar position="static" color="default" elevation={1} sx={{ backgroundColor: 'white' }}>
      <Toolbar>
        <Typography variant="h5" component="div" sx={{ fontWeight: 600 }}>
          Scova
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;