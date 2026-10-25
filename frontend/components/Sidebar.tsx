"use client";
import { BarChart3, LayoutDashboard, PlusCircle, Ticket } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const NAV = [
  { href: "/", label: "Queue", icon: LayoutDashboard },
  { href: "/tickets", label: "All tickets", icon: Ticket },
  { href: "/tickets/new", label: "New ticket", icon: PlusCircle },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
];

export default function Sidebar() {
  const path = usePathname();
  const [state, setState] = useState<"checking" | "up" | "down">("checking");
  const [model, setModel] = useState("");

  useEffect(() => {
    let alive = true;
    const ping = () => api.health()
      .then((h) => { if (alive) { setState("up"); setModel(h.models_loaded ? h.model_version : "rule fallback"); } })
      .catch(() => alive && setState("down"));
    ping();
    const t = setInterval(ping, 30000);
    return () => { alive = false; clearInterval(t); };
  }, []);

  const active = (href: string) => (href === "/" ? path === "/" : href === "/tickets" ? path === "/tickets" || /^\/tickets\/\d+/.test(path) : path.startsWith(href));

  return (
    <aside className="sidebar">
      <Link href="/" className="brand"><span className="brand-mark">SQ</span>SupportIQ</Link>
      <nav>
        {NAV.map(({ href, label, icon: Icon }) => (
          <Link key={href} href={href} className={active(href) ? "nav active" : "nav"}>
            <Icon size={18} aria-hidden />{label}
          </Link>
        ))}
      </nav>
      <div className="api-status">
        <span className={`pulse ${state}`} />
        <div>
          <div>{state === "up" ? "API online" : state === "down" ? "API unreachable" : "Checking API"}</div>
          {state === "up" && <div className="muted small">Model: {model}</div>}
          {state === "down" && <div className="muted small">Free hosts sleep; retry shortly</div>}
        </div>
      </div>
    </aside>
  );
}
