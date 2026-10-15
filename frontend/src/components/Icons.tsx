import type { SVGProps } from "react";

// Petite collection d'icônes SVG en ligne (aucune dépendance externe).
type IconProps = SVGProps<SVGSVGElement>;

const base: IconProps = {
  width: 20,
  height: 20,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
};

export function LogoMark(props: IconProps) {
  return (
    <svg width={28} height={28} viewBox="0 0 24 24" fill="none" aria-hidden {...props}>
      <defs>
        <linearGradient id="logo-grad" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
          <stop stopColor="#a78bfa" />
          <stop offset="1" stopColor="#22d3ee" />
        </linearGradient>
      </defs>
      <path
        d="M15 4v12.5a3.5 3.5 0 1 1-2-3.16V7l6-1.5v10.5a3.5 3.5 0 1 1-2-3.16"
        fill="url(#logo-grad)"
      />
    </svg>
  );
}

export function UploadCloud(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M12 13v8" />
      <path d="m8 17 4-4 4 4" />
      <path d="M20 16.6A4.5 4.5 0 0 0 17.5 8h-1.3A7 7 0 1 0 5 15.3" />
    </svg>
  );
}

export function Sparkles(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M12 3v4M12 17v4M3 12h4M17 12h4" />
      <path d="M12 8.5 13.2 11l2.5 1-2.5 1L12 15.5 10.8 13l-2.5-1 2.5-1L12 8.5Z" />
    </svg>
  );
}

export function Send(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M22 2 11 13" />
      <path d="M22 2 15 22l-4-9-9-4 20-7Z" />
    </svg>
  );
}

export function Activity(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M3 12h3l2.5-7 4 18 3-11h3l2-3h1" />
    </svg>
  );
}

export function Wand(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="m3 21 9-9" />
      <path d="M15 4V2M15 10V8M11.5 6.5h-2M20.5 6.5h-2M17.5 4.5l-1.5-1.5M17.5 8.5l-1.5 1.5M12.5 8.5l1.5 1.5M12.5 4.5l1.5-1.5" />
    </svg>
  );
}

export function Book(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" />
    </svg>
  );
}

export function Check(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="m20 6-11 11-5-5" />
    </svg>
  );
}

export function Info(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 16v-4M12 8h.01" />
    </svg>
  );
}

export function ArrowRight(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

export function Copy(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
      <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
    </svg>
  );
}

export function Music(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M9 18V5l12-2v13" />
      <circle cx="6" cy="18" r="3" />
      <circle cx="18" cy="16" r="3" />
    </svg>
  );
}

export function Chat(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z" />
    </svg>
  );
}
