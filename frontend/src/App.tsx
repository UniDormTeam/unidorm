import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage/LoginPage";
// [ADD]
import ReportFaultPage from "./pages/Dashboards/Student/ReportFaultPage";
import NewBookingPage from "./pages/Dashboards/Student/NewBookingPage";


/*موقتتت*/
import StudentDashboard from "./pages/Dashboards/Student/StudentDashboard"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<StudentDashboard />} />
        {/* [ADD] فرم‌های مستقل دانشجو */}
        <Route path="/dashboard/report-fault" element={<ReportFaultPage />}/>
        <Route path="/dashboard/new-booking" element={<NewBookingPage />}/>
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
