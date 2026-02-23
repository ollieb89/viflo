import { Box, Container, Typography, Button } from '@mui/material';
import Link from 'next/link';

export default function Home() {
  return (
    <Container maxWidth="lg">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          gap: 3,
        }}
      >
        <Typography variant="h1" component="h1" textAlign="center">
          Next.js App Template
        </Typography>
        
        <Typography variant="body1" color="text.secondary" textAlign="center">
          Built with Viflo frontend development guidelines
        </Typography>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="contained" component={Link} href="/dashboard">
            Get Started
          </Button>
          <Button variant="outlined" href="https://github.com">
            View on GitHub
          </Button>
        </Box>
      </Box>
    </Container>
  );
}
