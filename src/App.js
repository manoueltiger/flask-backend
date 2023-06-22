import './Stylesheet/App.css';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import { Route, RouterProvider, createBrowserRouter, createRoutesFromElements } from 'react-router-dom';
import Home from './pages/home/Home';
import ErrorPage from './components/ErrorPage';
import Dashboard from './pages/home/Dashboard';
import LandingPage from './pages/home/LandingPage';
import PrivateRoute from './components/PrivateRoute';
import { useDispatch } from 'react-redux';
import { useEffect } from 'react';
import { authSuccess } from './reducers/authReducer';
import EditPatient from './components/patient/EditPatient';
import Settings from './pages/Settings'
import Statistics from './pages/Statistics';
import Patients from './pages/Patients';
import Programs from './pages/Programs';
import RegisterConfirmation from './components/auth/RegisterConfirmation';


function App() {
  const dispatch = useDispatch();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      dispatch(authSuccess({token}));
    }
  }, [dispatch]);

  const router = createBrowserRouter(
    createRoutesFromElements(
      <>
        <Route path='/' element={<Home />} errorElement={<ErrorPage />} >
          <Route index element={<LoginForm />} />
          <Route path='/login' element={<LoginForm />} />
          <Route path='confirm/:token' element={< RegisterConfirmation />}/>
          <Route path='signup' element={<RegisterForm />} />
        </Route>
        <Route path='/dashboard' element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }>
            <Route index element={< LandingPage />} />
            <Route path='statistics' element={<Statistics />} />
            <Route path='patients' element={<Patients />}/>
            <Route path="patients/:patientId" element={<EditPatient />} />
            <Route path='programs' element={<Programs />} />
            <Route path='settings' element={<Settings />}/>
          </Route>  
      </>
    )
  )

  return (
    <div>
        <RouterProvider router={router} />
    </div>
  );
}

export default App;
