import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import WardrobePage from './pages/WardrobePage';
import UploadPage from './pages/UploadPage';
import RecommendPage from './pages/RecommendPage';
import NotFoundPage from './pages/NotFoundPage';
import ClothingDetailPage from './pages/ClothingDetailPage';
import LoginPage from './pages/LoginPage';
import PreferencesPage from './pages/PreferencesPage';
import FavoritesPage from './pages/FavoritesPage';
import AnalyticsPage from './pages/AnalyticsPage';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/wardrobe" element={<WardrobePage />} />
            <Route path="/wardrobe/:id" element={<ClothingDetailPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/recommend" element={<RecommendPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/preferences" element={<PreferencesPage />} />
            <Route path="/favorites" element={<FavoritesPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;
