// Central definition of all app routes
// Can also include metadata for navigation (e.g. labels, icons)

import { Home, CreditCard, List, Target, Settings } from "lucide-react"; 
// lucide-react = lightweight icon library (used a lot in production apps)

const routes = [
  {
    path: "/",
    name: "Dashboard",
    icon: Home,
    component: "Dashboard", // we’ll lazy load by name in Router.js
  },
  {
    path: "/accounts",
    name: "Accounts",
    icon: CreditCard,
    component: "Accounts",
  },
  {
    path: "/transactions",
    name: "Transactions",
    icon: List,
    component: "Transactions",
  },
  {
    path: "/insights",
    name: "Insights",
    icon: Target,
    component: "Insights",
  },
  {
    path: "/chat",
    name: "Chat",
    icon: Settings,
    component: "Chat",
  },
];

export default routes;
