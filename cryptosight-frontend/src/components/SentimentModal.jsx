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
        borderRadius: 2,
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
        
        <Box sx={{ p: 3 }}>
          {/* Social Media */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2">Social Media</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" fontWeight="medium">{socialMedia}%</Typography>
                <Typography variant="body2" sx={{ ml: 0.5, color: getTrendInfo(socialMedia).color }}>
                  {getTrendInfo(socialMedia).icon}
                </Typography>
              </Box>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={socialMedia} 
              color={socialMedia >= 60 ? "success" : socialMedia >= 40 ? "warning" : "error"}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
          
          {/* News Articles */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2">News Articles</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" fontWeight="medium">{newsArticles}%</Typography>
                <Typography variant="body2" sx={{ ml: 0.5, color: getTrendInfo(newsArticles).color }}>
                  {getTrendInfo(newsArticles).icon}
                </Typography>
              </Box>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={newsArticles} 
              color={newsArticles >= 60 ? "success" : newsArticles >= 40 ? "warning" : "error"}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
          
          {/* Trading Volume */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2">Trading Volume</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" fontWeight="medium">{tradingVolume}%</Typography>
                <Typography variant="body2" sx={{ ml: 0.5, color: getTrendInfo(tradingVolume).color }}>
                  {getTrendInfo(tradingVolume).icon}
                </Typography>
              </Box>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={tradingVolume} 
              color={tradingVolume >= 60 ? "success" : tradingVolume >= 40 ? "warning" : "error"}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
          
          {/* Market Volatility */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2">Market Volatility</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" fontWeight="medium">{marketVolatility}%</Typography>
                <Typography variant="body2" sx={{ ml: 0.5, color: getTrendInfo(marketVolatility).color }}>
                  {getTrendInfo(marketVolatility).icon}
                </Typography>
              </Box>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={marketVolatility} 
              color={marketVolatility >= 60 ? "success" : marketVolatility >= 40 ? "warning" : "error"}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
          
          {/* Institutional Interest */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2">Institutional Interest</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" fontWeight="medium">{institutionalInterest}%</Typography>
                <Typography variant="body2" sx={{ ml: 0.5, color: getTrendInfo(institutionalInterest).color }}>
                  {getTrendInfo(institutionalInterest).icon}
                </Typography>
              </Box>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={institutionalInterest} 
              color={institutionalInterest >= 60 ? "success" : institutionalInterest >= 40 ? "warning" : "error"}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
        </Box>
      </Box>
    </Modal>
  );
};

export default SentimentModal;