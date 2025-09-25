import React, { Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import routes from "./routes";

const loadPage = (pageName) =>
  React.lazy(() => import(`../pages/${pageName}.js`));

export default function AppRouter({ children }) {
  return (
    <BrowserRouter>
      {children}

      <main className="flex-1 bg-gray-50 p-4 overflow-y-auto">
        <Suspense fallback={<div>Loading...</div>}>
          <Routes>
            {routes.map(({ path, component }, index) => {
              const PageComponent = loadPage(component);
              return (
                <Route key={index} path={path} element={<PageComponent />} />
              );
            })}
          </Routes>
        </Suspense>
      </main>
    </BrowserRouter>
  );
}
