import React from 'react'
import App from './App'
import './index.css'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import './css/ToastStyles.css';  // Добавьте эту строку

import { createRoot } from 'react-dom/client'
const container = document.getElementById('root')
const root = createRoot(container)

root.render(
  <React.StrictMode>
    <ToastContainer
      position={"bottom-right"}
      autoClose={3000}
      hideProgressBar={true}
      newestOnTop={false}
      closeOnClick
      rtl={false}
      pauseOnFocusLoss
      draggable
    />
    <App />
  </React.StrictMode>
)
