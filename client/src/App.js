import logo from './logo.svg';
import './App.css';
import { AppBar, Toolbar } from "@material-ui/core";
import {
  BrowserRouter as Router
} from "react-router-dom";
import RouterSwitch from './router-switch';
import Header from "./components/header";

function App() {
  return (
    <Router>
      <Header />
      <RouterSwitch />
      
    </Router>
  );
}

export default App;
