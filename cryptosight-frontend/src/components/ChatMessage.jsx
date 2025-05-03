// src/components/ChatMessage.jsx
import React, { useState } from 'react';
import { Box, Typography, Paper, Chip, Button } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import SourceIcon from '@mui/icons-material/Source';
import SentimentModal from './SentimentModal';
import SourcesModal from './SourcesModal';

const ChatMessage = ({ message }) => {
  const [showSentimentModal, setShowSentimentModal] = useState(false);
  const [showSourcesModal, setShowSourcesModal] = useState(false);
  
  const isUser = message.role === 'user';
  
  // Split message content into paragraphs for better formatting
  const paragraphs = message.content.split('\n').filter(para => para.trim() !== '');
  
  return (
    <Box sx={{ 
      mb: 3, 
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start' // Position user messages to right, assistant to left
    }}>
      {/* Only show avatar for assistant messages on the left */}
      {!isUser && (
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            bgcolor: '#e0e0e0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold',
            mr: 1.5
          }}
        >
          C
        </Box>
      )}
      
      <Box sx={{ maxWidth: '75%' }}>
        <Paper 
          elevation={1}
          sx={{ 
            p: 2.5, 
            borderRadius: 8,
            backgroundColor: isUser ? '#D4AF37' : '#f8f9fa',
            color: isUser ? 'white' : 'black' 
          }}
        >
          {/* Format message content as paragraphs */}
          {paragraphs.map((paragraph, index) => {
            // Check if paragraph is a numbered point
            const isNumberedPoint = /^\d+\.\s/.test(paragraph);
            
            return (
              <Typography 
                key={index} 
                variant="body1" 
                component="div"
                sx={{ 
                  mb: index < paragraphs.length - 1 ? 1.5 : 0,
                  fontWeight: isNumberedPoint ? 500 : 400,
                  lineHeight: 1.6
                }}
              >
                {paragraph}
              </Typography>
            );
          })}
        </Paper>
        
        {!isUser && message.sentimentScore && (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1.5 }}>
            <Button 
              variant="outlined"
              size="small"
              startIcon={<InfoIcon />}
              onClick={() => setShowSentimentModal(true)}
              sx={{ 
                borderRadius: 5,
                textTransform: 'none',
                borderColor: '#e0e0e0',
                color: 'text.secondary',
                px: 1.5,
                py: 0.5
              }}
            >
              Market Sentiment
              <Box 
                sx={{ 
                  ml: 1,
                  width: 80,
                  height: 8,
                  bgcolor: '#e0e0e0',
                  borderRadius: 4,
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                <Box 
                  sx={{ 
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    height: '100%',
                    width: `${message.sentimentScore}%`,
                    bgcolor: message.sentimentScore >= 60 ? '#4caf50' : 
                            message.sentimentScore >= 40 ? '#f7b84b' : '#f44336'
                  }}
                />
              </Box>
              <Typography variant="caption" sx={{ ml: 0.5, fontWeight: 600 }}>
                {message.sentimentScore}
              </Typography>
            </Button>
            
            {message.sources && message.sources.length > 0 && (
              <Button
                variant="outlined"
                size="small"
                startIcon={<SourceIcon />}
                onClick={() => setShowSourcesModal(true)}
                sx={{ 
                  borderRadius: 5,
                  textTransform: 'none',
                  borderColor: '#e0e0e0',
                  color: 'text.secondary',
                  px: 1.5,
                  py: 0.5
                }}
              >
                Sources
                <Chip 
                  label={message.sources.length} 
                  size="small" 
                  sx={{ 
                    ml: 1, 
                    height: 20, 
                    fontSize: '0.7rem',
                    fontWeight: 600 
                  }}
                />
              </Button>
            )}
          </Box>
        )}
      </Box>
      
      {/* Show avatar for user messages on the right */}
      {isUser && (
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            bgcolor: '#D4AF37',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold',
            ml: 1.5 // margin-left instead of margin-right
          }}
        >
          U
        </Box>
      )}
      
      {/* Modals */}
      <SentimentModal 
        open={showSentimentModal}
        onClose={() => setShowSentimentModal(false)}
        sentimentScore={message.sentimentScore}
      />
      
      <SourcesModal 
        open={showSourcesModal}
        onClose={() => setShowSourcesModal(false)}
        sources={message.sources}
      />
    </Box>
  );
};

export default ChatMessage;