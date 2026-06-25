import { useState } from 'react';
import { Container, Typography, Tabs, Tab } from '@mui/material';
import BuildingsTab from '../components/admin/BuildingsTab';
import RoomTypesTab from '../components/admin/RoomTypesTab';
import RoomsTab from '../components/admin/RoomsTab';

export default function AdminPage() {
  const [tab, setTab] = useState(0);

  return (
    <Container sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Admin Panel
      </Typography>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
        <Tab label="Buildings" />
        <Tab label="Room Types" />
        <Tab label="Rooms" />
      </Tabs>

      {tab === 0 && <BuildingsTab />}
      {tab === 1 && <RoomTypesTab />}
      {tab === 2 && <RoomsTab />}
    </Container>
  );
}
