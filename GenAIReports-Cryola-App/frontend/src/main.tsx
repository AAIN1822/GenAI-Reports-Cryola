import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from "react-redux";
import { BrowserRouter } from 'react-router-dom';
import { PublicClientApplication } from "@azure/msal-browser";
import {msalConfig} from './config/msalConfig';
import { MsalProvider } from "@azure/msal-react";
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme/muiTheme';
import { store } from "./redux/store/index.ts";
import App from './App.tsx'
import './index.css'
import { ThemeProvider } from '@mui/material/styles';

const msalInstance = new PublicClientApplication(msalConfig);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
           <MsalProvider instance={msalInstance}>
            <App />
          </MsalProvider>
        </ThemeProvider>
      </Provider>
    </BrowserRouter>
  </StrictMode>,
)
