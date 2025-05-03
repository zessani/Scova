// src/components/SentimentModal.jsx
import React from 'react';
import { 
  Modal, 
  Box, 
  Typography, 
  IconButton,
  LinearProgress,
  Divider
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

// Function to determine trend direction and color
const getTrendInfo = (score) => {
  if (score > 70) return { icon: '↑', color: '#4caf50' };
  if (score < 50) return { icon: '↓', color: '#f44336' };
  return { icon: '→', color: '#f7b84b' };
};

const SentimentModal = ({ open, onClose, sentimentScore }) => {
  if (!sentimentScore) return null;
  
  // Example sentiment scores for different categories
  const socialMedia = 82;
  const newsArticles = 68;
  const tradingVolume = 79;
  const marketVolatility = 63;
  const institutionalInterest = 85;
  
  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="sentiment-modal-title"
    >
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: { xs: '90%', sm: 500 },
        maxHeight: '90vh',
        bgcolor: 'background.paper',
        borderRadius: 6,
        boxShadow: 24,
        overflow: 'auto'
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2, borderBottom: '1px solid #e0e0e0' }}>
          <Typography id="sentiment-modal-title" variant="h6" component="h2">
            Market Sentiment Analysis
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
          <Typography variant="h2" sx={{ fontWeight: 'bold', color: '#4caf50' }}>
            {sentimentScore}%
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Overall Positive Sentiment
          </Typography>
        </Box>
        
        <Divider />
        
        </Box>
    </Modal>
  );
};

export default SentimentModal;