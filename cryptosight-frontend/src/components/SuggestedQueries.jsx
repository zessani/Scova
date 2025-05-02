// src/components/SuggestedQueries.jsx
import React from 'react';
import { Box, Typography, Button } from '@mui/material';

const SuggestedQueries = ({ onSuggestionClick }) => {
  const suggestions = [
    "Analyze Bitcoin's current market status",
    "What's happening with Ethereum?",
    "Show me the latest analysis for Solana",
    "What's the market sentiment for Cardano?"
  ];

  return (
    <Box sx={{ my: 3 }}>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
        Try asking:
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {suggestions.map((suggestion, index) => (
          <Button 
            key={index} 
            variant="outlined"
            onClick={() => onSuggestionClick(suggestion)}
            sx={{ 
              textTransform: 'none', 
              borderRadius: 5,
              borderColor: '#e0e0e0',
              color: 'text.primary',
              '&:hover': {
                borderColor: '#f7b84b',
                color: '#f7b84b'
              }
            }}
          >
            {suggestion}
          </Button>
        ))}
      </Box>
    </Box>
  );
};

export default SuggestedQueries;