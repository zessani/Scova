// src/services/ApiService.js
import axios from 'axios';

// Create an axios instance with the base URL
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

const ApiService = {
  // Get analysis for a cryptocurrency
  async getAnalysis(symbol) {
    try {
      const response = await api.get(`/analyze/${symbol}`);
      return response.data;
    } catch (error) {
      console.error(`Error analyzing ${symbol}:`, error);
      throw error;
    }
  },

  // Handle follow-up questions
  async getFollowup(symbol, question) {
    try {
      const response = await api.post('/followup', {
        symbol,
        question
      });
      return response.data;
    } catch (error) {
      console.error('Error handling follow-up:', error);
      throw error;
    }
  },

  // Get price prediction
  async getPrediction(symbol, timeframe = 'month') {
    try {
      const response = await api.post('/predict', {
        symbol,
        timeframe
      });
      return response.data;
    } catch (error) {
      console.error('Error generating prediction:', error);
      throw error;
    }
  },

  // Get trading strategy
  async getTradingStrategy(symbol, goal) {
    try {
      const response = await api.post('/strategy', {
        symbol,
        goal
      });
      return response.data;
    } catch (error) {
      console.error('Error generating strategy:', error);
      throw error;
    }
  },

  // Analyze policy impact
  async getPolicyImpact(symbol, policyDescription) {
    try {
      const response = await api.post('/policy-impact', {
        symbol,
        policy_description: policyDescription
      });
      return response.data;
    } catch (error) {
      console.error('Error analyzing policy impact:', error);
      throw error;
    }
  }
};

export default ApiService;