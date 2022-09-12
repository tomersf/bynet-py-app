import logo from "./logo.svg";
import "./App.css";
import axios from 'axios'
import StudentsList from "./components/StudentsList";

function App() {
  return (
    <div className="App">
      <StudentsList/>
    </div>
  );
}

export default App;
