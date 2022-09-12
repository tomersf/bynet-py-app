import React from "react";
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

const bull = (
  <Box
    component="span"
    sx={{ display: 'inline-block', mx: '2px', transform: 'scale(0.8)' }}
  >
    •
  </Box>
);

export default function StudentCard(props) {
  const {name,attendance_duration,attendance_percentage} = props.student;
  return (
    <Box sx={{ minWidth: 275 }}>
    <Card variant="outlined">
    <React.Fragment>
    <CardContent>
      <Typography sx={{ fontSize: 14 }} color="text.secondary" gutterBottom>
       {name}
      </Typography>
      <Typography variant="h5" component="div">
        {attendance_duration}
      </Typography>
      <Typography sx={{ mb: 1.5 }} color="text.secondary">
        {attendance_percentage}
      </Typography>
    </CardContent>
  </React.Fragment>
    </Card>
  </Box>
  );
}