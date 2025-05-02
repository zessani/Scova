import React from 'react';
import { Box } from '@mui/material';

const Loading = () => {
  return (
    <Box sx={{ display: 'flex', my: 2, ml: 5 }}>
      <Box
        sx={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          bgcolor: 'grey.400',
          mx: 0.5,
          animation: 'pulse 1.5s infinite',
        }}
      />
      <Box
        sx={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          bgcolor: 'grey.400',
          mx: 0.5,
          animation: 'pulse 1.5s infinite',
          animationDelay: '0.2s'
        }}
      />
      <Box
        sx={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          bgcolor: 'grey.400',
          mx: 0.5,
          animation: 'pulse 1.5s infinite',
          animationDelay: '0.4s'
        }}
      />
    </Box>
  );
};

export default Loading;