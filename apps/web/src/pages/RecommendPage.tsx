export default function RecommendPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">穿搭推荐</h1>
        <p className="mt-1 text-sm text-gray-500">
          告诉我们您要去哪，或者直接获取每日推荐。
        </p>
      </div>

      <div className="bg-white shadow-sm rounded-lg border border-gray-100 p-6">
        <form className="space-y-6">
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-3">
            <div>
              <label htmlFor="city" className="block text-sm font-medium text-gray-700">城市</label>
              <select id="city" name="city" className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-brand-500 focus:border-brand-500 sm:text-sm rounded-md">
                <option>北京</option>
                <option>上海</option>
                <option>广州</option>
                <option>深圳</option>
                <option>杭州</option>
              </select>
            </div>

            <div>
              <label htmlFor="scene" className="block text-sm font-medium text-gray-700">场景</label>
              <select id="scene" name="scene" className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-brand-500 focus:border-brand-500 sm:text-sm rounded-md">
                <option>日常通勤</option>
                <option>约会</option>
                <option>运动健身</option>
                <option>休闲逛街</option>
                <option>正式会议</option>
              </select>
            </div>

            <div>
              <label htmlFor="style" className="block text-sm font-medium text-gray-700">偏好风格</label>
              <select id="style" name="style" className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-brand-500 focus:border-brand-500 sm:text-sm rounded-md">
                <option>简约</option>
                <option>商务</option>
                <option>休闲</option>
                <option>日系</option>
                <option>复古</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <button type="button" className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-brand-600 hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500">
              获取推荐
            </button>
          </div>
        </form>
      </div>

      <div className="mt-8 text-center text-gray-500 py-12 bg-white rounded-lg border border-dashed border-gray-300">
        点击上方按钮，AI 将为您生成专属穿搭方案
      </div>
    </div>
  );
}
