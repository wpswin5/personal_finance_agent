// Central definition of all app routes
// Can also include metadata for navigation (e.g. labels, icons)

import { Home, CreditCard, Users, MessageCircle, User } from "lucide-react";

// Simplified app routes for the rough-draft frontend
const routes = [
  { path: "/", name: "Dashboard", icon: Home, component: "Dashboard" },
  { path: "/accounts", name: "Accounts", icon: CreditCard, component: "Accounts" },
  { path: "/households", name: "Households", icon: Users, component: "Households" },
  { path: "/agent", name: "Agent", icon: MessageCircle, component: "Agent" },
  { path: "/profile", name: "Profile", icon: User, component: "Profile" },
];

export default routes;
