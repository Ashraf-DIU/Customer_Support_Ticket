"use client";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts";
import type { Count } from "@/lib/types";

const PRIORITY_COLORS: Record<string, string> = { Critical: "#C23B2E", High: "#D9782B", Medium: "#C4A02A", Low: "#2F8F6B" };
const SENTIMENT_COLORS: Record<string, string> = { Negative: "#C23B2E", Neutral: "#7C8794", Positive: "#2F8F6B" };
const BLUE = "#2250C4";

export function HBar({ data }: { data: Count[] }) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(180, data.length * 42)}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16 }}>
        <CartesianGrid horizontal={false} stroke="#e4e8ee" />
        <XAxis type="number" allowDecimals={false} />
        <YAxis type="category" dataKey="label" width={130} tick={{ fontSize: 13 }} />
        <Tooltip cursor={{ fill: "rgba(34,80,196,.06)" }} />
        <Bar dataKey="count" fill={BLUE} radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function Donut({ data, kind }: { data: Count[]; kind: "priority" | "sentiment" }) {
  const colors = kind === "priority" ? PRIORITY_COLORS : SENTIMENT_COLORS;
  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie data={data} dataKey="count" nameKey="label" innerRadius={55} outerRadius={90} paddingAngle={2}>
          {data.map((d) => <Cell key={d.label} fill={colors[d.label] ?? "#7C8794"} />)}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function Trend({ data }: { data: { date: string; count: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={data} margin={{ left: -16, right: 8 }}>
        <CartesianGrid vertical={false} stroke="#e4e8ee" />
        <XAxis dataKey="date" tickFormatter={(d: string) => d.slice(5)} tick={{ fontSize: 12 }} />
        <YAxis allowDecimals={false} />
        <Tooltip />
        <Line type="monotone" dataKey="count" name="Tickets" stroke={BLUE} strokeWidth={2.5} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
