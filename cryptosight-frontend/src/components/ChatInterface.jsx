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
  const symbolMatch = input.match(/\b(BTC|ETH|SOL|ADA|XRP|DOT|LINK|LTC)\b/i);
  
  if (symbolMatch) {
    return symbolMatch[0].toUpperCase();
  }
  
  // Name to symbol mapping
  const nameMap = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'solana': 'SOL',
    'cardano': 'ADA',
    'ripple': 'XRP',
    'polkadot': 'DOT',
    'chainlink': 'LINK',
    'litecoin': 'LTC'
  };
  
  // Check for crypto name (e.g., "bitcoin", "ethereum")
  for (const [name, symbol] of Object.entries(nameMap)) {
    if (input.toLowerCase().includes(name)) {
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
  const messagesEndRef = useRef(null);
  
  // Auto scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // In your handleSubmit function
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
      // Extract crypto symbol from input
      const symbol = extractCryptoSymbol(input);
      
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
        } else if (input.toLowerCase().startsWith(symbol.toLowerCase()) || 
                  input.toLowerCase().startsWith(`analyze ${symbol.toLowerCase()}`)) {
          // For direct analysis requests, we've already called this above,
          // but we need the response data
          response = await ApiService.getAnalysis(symbol);
        } else {
          // For follow-up questions
          response = await ApiService.getFollowup(symbol, input);
        }
      } else {
        // Generic response for questions not about specific cryptos
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
  
  return (
    <Box sx={{ mb: 3 }}>
      {/* Floating chat container with shadow - matching header design */}
      <Box 
        sx={{ 
          backgroundColor: 'white',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.12)',  // Stronger shadow
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
          
          <div ref={messagesEndRef} />
        </Box>
        
        <Box 
          component="form" 
          onSubmit={handleSubmit}
          sx={{ 
            p: 2, 
            borderTop: '1px solid #e0e0e0',
            bgcolor: '#f8f9fa',
          }}
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
                pr: 0.5,
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: ''
                }
              }
            }}
          />
        </Box>
        
        <Box sx={{ p: 1, textAlign: 'center', borderTop: '1px solid rgba(0,0,0,0.03)' }}>
          <Typography variant="caption" color="text.secondary">
            All market analysis is for informational purposes only
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default ChatInterface;