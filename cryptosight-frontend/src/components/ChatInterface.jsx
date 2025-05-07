// src/components/ChatInterface.jsx
import React, { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  TextField, 
  IconButton, 
  Typography,
  InputAdornment
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ChatMessage from './ChatMessage';
import SuggestedQueries from './SuggestedQueries';
import Loading from './Loading';
import ApiService from '../services/ApiService';

// Helper to extract crypto symbol from user input
const extractCryptoSymbol = (input) => {
  // Direct symbol match (e.g., "BTC", "ETH")
  const symbolMatch = input.match(/\b(BTC|ETH|SOL|ADA|XRP|DOT|LINK|LTC|DOGE|AVAX|MATIC|UNI|SHIB)\b/i);
  
  if (symbolMatch) {
    return symbolMatch[0].toUpperCase();
  }
  
  // Name to symbol mapping with expanded cryptocurrencies
  const nameMap = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'solana': 'SOL',
    'cardano': 'ADA',
    'ripple': 'XRP',
    'polkadot': 'DOT',
    'chainlink': 'LINK',
    'litecoin': 'LTC',
    'dogecoin': 'DOGE',
    'doge': 'DOGE',
    'avalanche': 'AVAX',
    'polygon': 'MATIC',
    'uniswap': 'UNI',
    'shiba': 'SHIB'
  };
  
  // Check for crypto name (e.g., "bitcoin", "ethereum")
  for (const [name, symbol] of Object.entries(nameMap)) {
    if (input.toLowerCase().includes(name.toLowerCase())) {
      return symbol;
    }
  }
  
  return null;
};

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello, I'm your crypto analysis assistant. I can help you understand market trends, analyze specific cryptocurrencies, and provide insights about the blockchain ecosystem. How can I assist you today?",
      sentimentScore: null,
      sources: [],
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentSymbol, setCurrentSymbol] = useState(null); // Track the current cryptocurrency being discussed
  const messagesEndRef = useRef(null);
  
  // Auto scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;
    
    // Add user message
    const userMessage = {
      role: 'user',
      content: input,
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    
    try {
      // Try to detect cryptocurrency in the input
      const detectedSymbol = extractCryptoSymbol(input);
      
      // If we found a symbol in the current message, update our context
      if (detectedSymbol) {
        // Only update if it's different from current symbol to avoid unnecessary re-renders
        if (detectedSymbol !== currentSymbol) {
          console.log(`Switching context from ${currentSymbol} to ${detectedSymbol}`);
          setCurrentSymbol(detectedSymbol);
        }
      }
      
      // Use either the detected symbol or the current context symbol
      const symbol = detectedSymbol || currentSymbol;
      
      let response;
      
      if (symbol) {
        // IMPORTANT: Always get analysis first to populate the cache
        try {
          await ApiService.getAnalysis(symbol);
          console.log(`Analysis cache populated for ${symbol}`);
        } catch (analysisError) {
          console.log(`Note: Could not pre-load analysis: ${analysisError.message}`);
          // Continue anyway, as we'll handle specific endpoints next
        }
        
        // Now proceed with the specific API calls based on the query type
        if (input.match(/when should|strategy|timing|best time|maximize|predict|forecast/i)) {
          response = await ApiService.getTradingStrategy(symbol, input);
        } else if (input.match(/policy|regulation|impact|affect/i)) {
          response = await ApiService.getPolicyImpact(symbol, input);
        } else if (
          (detectedSymbol && input.toLowerCase().startsWith(detectedSymbol.toLowerCase())) || 
          (detectedSymbol && input.toLowerCase().startsWith(`analyze ${detectedSymbol.toLowerCase()}`))
        ) {
          // For direct analysis requests with the symbol explicitly mentioned
          response = await ApiService.getAnalysis(symbol);
        } else {
          // For follow-up questions or when symbol is from context
          response = await ApiService.getFollowup(symbol, input);
        }
      } else {
        // Generic response for questions with no crypto context
        response = {
          response: "I can provide you with analysis on specific cryptocurrencies like Bitcoin (BTC), Ethereum (ETH), Solana (SOL), and more. Please ask about a specific cryptocurrency to get detailed insights.",
          sentiment_score: null,
          sources: []
        };
      }
      
      // Add assistant message with the response
      const assistantMessage = {
        role: 'assistant',
        content: response.response || response.combined_analysis || response.strategy || 
                response.prediction || response.impact_analysis || 
                "I couldn't analyze that. Please try asking about a specific cryptocurrency.",
        sentimentScore: response.sentiment_score,
        sources: response.sources || [],
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error fetching response:', error);
      
      // Add error message
      const errorMessage = {
        role: 'assistant',
        content: "I'm sorry, but I encountered an error while analyzing that. Please try again or ask about another cryptocurrency.",
        sentimentScore: null,
        sources: [],
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    // Optionally auto-submit the suggestion
    setTimeout(() => {
      handleSubmit();
    }, 100);
  };
  
  // Debug function to show current context in the console
  useEffect(() => {
    console.log(`Current crypto context: ${currentSymbol || 'None'}`);
  }, [currentSymbol]);
  
  return (
    <Box sx={{ mb: 3 }}>
      {/* Floating chat container with shadow - matching header design */}
      <Box 
        sx={{ 
          backgroundColor: 'white',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.14)',  // Stronger shadow
          borderRadius: 4,  // Rounder edges
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          height: '80vh',
          position: 'relative',
          zIndex: 5
        }}
      >
        <Box 
          sx={{ 
            flex: 1, 
            overflow: 'auto', 
            p: 3
          }}
        >
          {messages.map((message, index) => (
            <ChatMessage 
              key={index}
              message={message}
            />
          ))}
          
          {/* Show loading indicator when waiting for a response */}
          {loading && <Loading />}
          
          {/* Only show suggestions if there's exactly one message */}
          {messages.length === 1 && (
            <SuggestedQueries onSuggestionClick={handleSuggestionClick} />
          )}
          
          {/* Current context indicator (optional - can be removed or styled differently) */}
          {currentSymbol && (
            <Box sx={{ 
              position: 'absolute', 
              top: 10, 
              right: 10, 
              bgcolor: 'rgba(212, 175, 55, 0.1)', 
              borderRadius: 10,
              px: 2,
              py: 0.5,
              fontSize: '0.75rem',
              color: 'text.secondary'
            }}>
              Currently discussing: {currentSymbol}
            </Box>
          )}
          
          <div ref={messagesEndRef} />
        </Box>
        
        <Box 
          component="form" 
          onSubmit={handleSubmit}
          sx={{ p: 2 }}
        >
          <TextField
            fullWidth
            placeholder="Ask about crypto markets, analysis, or trends..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            variant="outlined"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton 
                    color="primary" 
                    type="submit"
                    disabled={loading || !input.trim()}
                    sx={{ bgcolor: '#D4AF37', color: 'white', '&:hover': { bgcolor: '#e0a73e' } }}
                  >
                    <SendIcon />
                  </IconButton>
                </InputAdornment>
              ),
              sx: { 
                borderRadius: 5,
                bgcolor: '#f8f9fa',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.14)',
                pr: 0.5,
                '& .MuiOutlinedInput-notchedOutline': {
                  // Border styling if needed
                }
              }
            }}
          />
        </Box>
        
        <Box sx={{ p: 1, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            All market analysis is for informational purposes only
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default ChatInterface;