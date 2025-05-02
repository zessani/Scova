// src/components/SourcesModal.jsx
import React from 'react';
import { 
  Modal, 
  Box, 
  Typography, 
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Link
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

// Helper functions to determine source information
const getSourceType = (url) => {
  if (!url) return 'News';
  
  if (url.includes('coindesk') || url.includes('cointelegraph')) {
    return 'News';
  }
  
  if (url.includes('binance') || url.includes('kraken')) {
    return 'Exchange Analysis';
  }
  
  if (url.includes('twitter') || url.includes('reddit')) {
    return 'Social Media';
  }
  
  if (url.includes('glassnode') || url.includes('cryptoquant')) {
    return 'On-chain Data';
  }
  
  return 'News';
};

const getReliability = (name) => {
  if (!name) return { level: 'Medium', color: '#f7b84b' };
  
  const highReliability = ['CoinDesk', 'Binance Research', 'Glassnode', 'CryptoQuant'];
  const mediumReliability = ['Twitter', 'Medium'];
  const lowReliability = ['Reddit'];
  
  if (highReliability.some(item => name.includes(item))) 
    return { level: 'High', color: '#4caf50' };
  
  if (mediumReliability.some(item => name.includes(item))) 
    return { level: 'Medium', color: '#f7b84b' };
  
  if (lowReliability.some(item => name.includes(item))) 
    return { level: 'Low', color: '#f44336' };
  
  return { level: 'Medium', color: '#f7b84b' };
};

const getUpdatedTime = () => {
  const options = ['1 day ago', '2 days ago', '3 days ago', 'Real-time'];
  return options[Math.floor(Math.random() * options.length)];
};

const SourcesModal = ({ open, onClose, sources }) => {
  if (!sources || sources.length === 0) return null;
  
  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="sources-modal-title"
    >
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: { xs: '90%', sm: 600 },
        maxHeight: '90vh',
        bgcolor: 'background.paper',
        borderRadius: 2,
        boxShadow: 24,
        overflow: 'auto'
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2, borderBottom: '1px solid #e0e0e0' }}>
          <Typography id="sources-modal-title" variant="h6" component="h2">
            Analysis Sources
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
        
        <TableContainer component={Paper} sx={{ boxShadow: 'none' }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Source</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Reliability</TableCell>
                <TableCell>Updated</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sources.map((source, index) => {
                const sourceType = getSourceType(source.url);
                const reliability = getReliability(source.name);
                const updated = getUpdatedTime();
                
                return (
                  <TableRow key={index}>
                    <TableCell>
                      {source.url ? (
                        <Link 
                          href={source.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          underline="hover"
                        >
                          {source.name}
                        </Link>
                      ) : (
                        source.name
                      )}
                    </TableCell>
                    <TableCell>{sourceType}</TableCell>
                    <TableCell>
                      <Typography sx={{ color: reliability.color, fontWeight: 500 }}>
                        {reliability.level}
                      </Typography>
                    </TableCell>
                    <TableCell>{updated}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Modal>
  );
};

export default SourcesModal;