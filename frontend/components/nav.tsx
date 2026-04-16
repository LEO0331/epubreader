"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const ITEMS = [
  { href: "/", label: "Dashboard" },
  { href: "/ingest", label: "Ingest" },
  { href: "/query", label: "Query" },
  { href: "/collections", label: "Collections" },
  { href: "/settings", label: "Settings" },
];

export function Nav() {
  const pathname = usePathname();

  return (
    <nav className="nav">
      {ITEMS.map((item) => {
        const isActive = item.href === "/" ? pathname === "/" : pathname?.startsWith(item.href);
        return (
          <Link key={item.href} href={item.href} className={isActive ? "nav-link active" : "nav-link"}>
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
