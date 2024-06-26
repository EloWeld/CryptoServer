import axios from 'axios';

const instance = axios.create({
    baseURL: process.env.REACT_APP_NODE_ENV === 'dev' ? process.env.REACT_APP_DEV_API_BASE_URL : process.env.REACT_APP_API_BASE_URL,
    withCredentials: true,
});

export default instance;
