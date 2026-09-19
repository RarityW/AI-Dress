import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="min-h-[60vh] flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8">
      <div className="text-center">
        <h1 className="text-9xl font-extrabold text-brand-600">404</h1>
        <p className="mt-2 text-2xl font-bold text-gray-900 tracking-tight sm:text-3xl">页面未找到</p>
        <p className="mt-4 text-base text-gray-500">抱歉，我们找不到您要访问的页面。</p>
        <div className="mt-10">
          <Link to="/" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-brand-600 hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500">
            返回首页
          </Link>
        </div>
      </div>
    </div>
  );
}
