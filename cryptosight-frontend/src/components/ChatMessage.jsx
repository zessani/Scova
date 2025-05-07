// src/components/ChatMessage.jsx
import React, { useState } from 'react';
import { Box, Typography, Paper, Chip, Button } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import SourceIcon from '@mui/icons-material/Source';
import SaveIcon from '@mui/icons-material/Save';
import EmailIcon from '@mui/icons-material/Email';
import SentimentModal from './SentimentModal';
import SourcesModal from './SourcesModal';
import { jsPDF } from 'jspdf';

const ChatMessage = ({ message }) => {
  const [showSentimentModal, setShowSentimentModal] = useState(false);
  const [showSourcesModal, setShowSourcesModal] = useState(false);
  const [showSaveSuccess, setShowSaveSuccess] = useState(false);
  
  const isUser = message.role === 'user';
  const isWelcomeMessage = !isUser && message.content.includes("I'm your crypto analysis assistant");
  const hasAnalysis = !isUser && !isWelcomeMessage && message.content.length > 100;
  
  // Base button style
  const buttonStyle = {
    borderRadius: 20,
    textTransform: 'none',
    backgroundColor: '#f5f8fa', 
    color: '#4978cc',
    border: 'none',
    padding: '6px 14px',
    minWidth: 'auto',
    fontSize: '0.875rem',
    fontWeight: 500,
    boxShadow: 'none',
    margin: '0 4px',
    '&:hover': {
      backgroundColor: '#e8f0fe',
      boxShadow: 'none',
    }
  };

  // For the sentiment button specifically
  const sentimentButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#f6f6f7',
    color: '#333333',
    '&:hover': {
      backgroundColor: '#eeeeee',
      boxShadow: 'none',
    }
  };

  // For the sources button specifically
  const sourcesButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#f6f6f7',
    color: '#333333',
    '&:hover': {
      backgroundColor: '#eeeeee',
      boxShadow: 'none',
    }
  };
  
  // Function to handle saving analysis as PDF
  const handleSaveAnalysis = () => {
    // Still save to localStorage for history
    const savedAnalyses = JSON.parse(localStorage.getItem('scova-saved-analyses') || '[]');
    savedAnalyses.push({
      content: message.content,
      sentimentScore: message.sentimentScore,
      timestamp: new Date().toISOString(),
      id: Date.now()
    });
    localStorage.setItem('scova-saved-analyses', JSON.stringify(savedAnalyses));
    
    // Generate PDF
    const doc = new jsPDF();
    
    // Add Scova branding
    doc.setFontSize(22);
    doc.setTextColor('#D4AF37');
    doc.text('Scova Analysis Report', 20, 20);
    
    // Add date
    doc.setFontSize(12);
    doc.setTextColor('#8E9196');
    const today = new Date().toLocaleDateString();
    doc.text(`Generated on: ${today}`, 20, 30);
    
    // Add sentiment score if available
    if (message.sentimentScore) {
      doc.setFontSize(14);
      doc.setTextColor('#333333');
      doc.text(`Market Sentiment Score: ${message.sentimentScore}%`, 20, 40);
    }
    
    // Add divider
    doc.setDrawColor('#D4AF37');
    doc.line(20, 45, 190, 45);
    
    // Add content
    doc.setFontSize(12);
    doc.setTextColor('#333333');
    
    // Process the content to handle Markdown-style bold text for PDF
    const pdfContent = message.content.replace(/\*\*(.*?)\*\*/g, '$1');
    
    // Split content into paragraphs and add to PDF with proper spacing
    const paragraphs = pdfContent.split('\n').filter(para => para.trim() !== '');
    let yPosition = 55;
    
    paragraphs.forEach(paragraph => {
      // Create wrapped text - the splitTextToSize function handles line breaks
      const textLines = doc.splitTextToSize(paragraph, 170);
      
      // Add each line with proper spacing
      doc.text(textLines, 20, yPosition);
      
      // Move position for next paragraph (accounting for number of lines)
      yPosition += 7 * (textLines.length); // Reduced from 10 to 7 for less spacing
      
      // Add extra space between paragraphs - reduced from 5 to 2
      yPosition += 2;
      
      // If near bottom of page, create new page
      if (yPosition > 270) {
        doc.addPage();
        yPosition = 20;
      }
    });
    
    // Add footer with disclaimer
    const pageCount = doc.internal.getNumberOfPages();
    doc.setPage(pageCount);
    doc.setFontSize(10);
    doc.setTextColor('#8E9196');
    doc.text('This analysis is for informational purposes only.', 20, 280);
    
    // Save the PDF
    doc.save(`Scova-Analysis-${new Date().toISOString().slice(0,10)}.pdf`);
    
    // Show success message
    setShowSaveSuccess(true);
    setTimeout(() => setShowSaveSuccess(false), 3000);
  };
  
  // Function to handle emailing report
  const handleEmailReport = () => {
    const subject = `Scova Crypto Analysis Report`;
    const body = `Here's your Scova analysis:\n\n${message.content}`;
    window.open(`mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`);
  };
  
  // Format text with highlights for price changes and sentiment and bold text
  const formatWithHighlights = (text) => {
    // Replace patterns for highlighting
    return text
      .replace(/(\+\d+(\.\d+)?%|\d+(\.\d+)?% increase)/g, '<span class="highlight-positive">$&</span>')
      .replace(/(\-\d+(\.\d+)?%|\d+(\.\d+)?% decrease)/g, '<span class="highlight-negative">$&</span>')
      .replace(/(bullish|positive)/gi, '<span class="highlight-positive">$&</span>')
      .replace(/(bearish|negative)/gi, '<span class="highlight-negative">$&</span>')
      // Add support for bold text formatting
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  };
  
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
            bgcolor: '#D4AF37',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold',
            mr: 1.5
          }}
        >
          S
        </Box>
      )}
      
      <Box sx={{ maxWidth: '75%' }}>
        <Paper 
          elevation={1}
          sx={{ 
            p: 2.5, 
            borderRadius: 8,
            backgroundColor: isUser ? '#D4AF37' : '#F6F6F7',
            color: isUser ? 'white' : '#333333' 
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
                  lineHeight: 1.6,
                  color: isUser ? 'white' : '#333333'
                }}
                dangerouslySetInnerHTML={{ 
                  __html: formatWithHighlights(paragraph) 
                }}
              />
            );
          })}
        </Paper>
        
        {/* Only show action buttons when we have actual analysis content */}
        {hasAnalysis && (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1.5 }}>
            {/* Sentiment button - only show if sentiment score is available */}
            {message.sentimentScore && (
              <Button 
                variant="contained"
                disableElevation
                startIcon={<Box
                  component="span"
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%', 
                    backgroundColor: '#2e7d32',
                    marginRight: '6px'
                  }}
                />}
                onClick={() => setShowSentimentModal(true)}
                sx={sentimentButtonStyle}
              >
                Market Sentiment
              </Button>
            )}
            
            {/* Sources button - only show if sources are available */}
            {message.sources && message.sources.length > 0 && (
              <Button
                variant="contained"
                disableElevation
                startIcon={<SourceIcon sx={{ fontSize: '1rem' }} />}
                onClick={() => setShowSourcesModal(true)}
                sx={sourcesButtonStyle}
              >
                Sources
              </Button>
            )}
            
            {/* Save Analysis button - always show for analysis messages */}
            <Button
              variant="contained"
              disableElevation
              startIcon={<SaveIcon sx={{ fontSize: '1rem' }} />}
              onClick={handleSaveAnalysis}
              sx={buttonStyle}
            >
              Save Analysis
            </Button>
            
            {/* Email Report button - always show for analysis messages */}
            <Button
              variant="contained"
              disableElevation
              startIcon={<EmailIcon sx={{ fontSize: '1rem' }} />}
              onClick={handleEmailReport}
              sx={buttonStyle}
            >
              Email Report
            </Button>
            
            {/* Success message */}
            {showSaveSuccess && (
              <Chip 
                label="Analysis saved!" 
                size="small" 
                className="save-success"
                sx={{ 
                  ml: 1,
                  fontWeight: 500,
                  borderColor: '#D4AF37',
                  color: '#D4AF37', 
                  backgroundColor: '#F5EED7'
                }}
              />
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