/**
 * Maps a source URL to a source type
 * @param {string} url - The source URL
 * @returns {string} - The source type
 */
export const getSourceType = (url) => {
    if (!url) return 'News';
    
    if (url.includes('coindesk') || url.includes('cointelegraph') || url.includes('bitcoin.com')) {
      return 'News';
    }
    
    if (url.includes('binance') || url.includes('kraken') || url.includes('coinbase')) {
      return 'Exchange Analysis';
    }
    
    if (url.includes('twitter') || url.includes('reddit') || url.includes('medium')) {
      return 'Social Media';
    }
    
    if (url.includes('glassnode') || url.includes('cryptoquant') || url.includes('blockchair')) {
      return 'On-chain Data';
    }
    
    return 'News';
  };
  
  /**
   * Maps a source name to a reliability rating
   * @param {string} name - The source name
   * @returns {string} - The reliability rating (High, Medium, Low)
   */
  export const getReliability = (name) => {
    if (!name) return 'Medium';
    
    const highReliability = ['CoinDesk', 'Binance Research', 'Glassnode', 'CryptoQuant', 
                            'Bloomberg', 'CoinMetrics', 'Chainalysis'];
                            
    const mediumReliability = ['Twitter', 'Medium', 'CoinTelegraph', 'Decrypt', 'BeInCrypto'];
    
    const lowReliability = ['Reddit', 'Telegram', 'Anonymous', '4chan'];
    
    if (highReliability.some(item => name.includes(item))) return 'High';
    if (mediumReliability.some(item => name.includes(item))) return 'Medium';
    if (lowReliability.some(item => name.includes(item))) return 'Low';
    
    return 'Medium';
  };
  
  /**
   * Generates a realistic "updated" timestamp 
   * @returns {string} - A human-readable timestamp
   */
  export const getUpdatedTime = () => {
    const options = ['1 day ago', '2 days ago', '3 days ago', 'Real-time'];
    return options[Math.floor(Math.random() * options.length)];
  };
  
  /**
   * Extracts cryptocurrency symbol from user input
   * @param {string} input - User input text
   * @returns {string|null} - Extracted symbol or null if not found
   */
  export const extractCryptoSymbol = (input) => {
    // Direct symbol match (e.g., "BTC", "ETH")
    const symbolMatch = input.match(/\b(BTC|ETH|SOL|ADA|XRP|DOT|LINK|LTC|DOGE|AVAX|MATIC|UNI|SHIB)\b/i);
    
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
      'litecoin': 'LTC',
      'dogecoin': 'DOGE',
      'avalanche': 'AVAX',
      'polygon': 'MATIC',
      'uniswap': 'UNI',
      'shiba': 'SHIB'
    };
    
    // Check for crypto name (e.g., "bitcoin", "ethereum")
    for (const [name, symbol] of Object.entries(nameMap)) {
      if (input.toLowerCase().includes(name)) {
        return symbol;
      }
    }
    
    return null;
  };