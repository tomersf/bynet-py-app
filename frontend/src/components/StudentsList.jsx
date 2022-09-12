import React, {useState,useEffect} from 'react'
import Grid from '@mui/material/Grid';

import axios from 'axios';
import StudentCard from './StudentCard';

export default function StudentsList() {
    const [studentsList,setStudentsList] = useState([])

    const fetchStudents = async () => {
        const students = await axios.get('http://localhost:5002/attendees');
        setStudentsList(students.data);
    }

    useEffect(() => fetchStudents,[]);

  return (
        <Grid container justifyContent="center" spacing={6}>
          {studentsList.map((student) => (
            <Grid key={student.id} item>
              <StudentCard
              student={student}
              />
            </Grid>
          ))}
        </Grid>
  );
}
