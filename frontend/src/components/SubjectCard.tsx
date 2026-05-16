import React from "react";
import type { Subject } from "../types";
import { API_URL } from "../config";

interface SubjectCardProps {
    subject: Subject;
    onSubjectsUpdate: (subjects: Subject[]) => void;
}

const SubjectCard: React.FC<SubjectCardProps> = ({ subject, onSubjectsUpdate }) => {
    const max = Math.floor(subject.totalHours * 0.3);
    const perc = max > 0 ? (subject.skipped / max) * 100 : 0;

    const getColorClass = () => {
        if (perc >= 60) return "red";
        if (perc >= 50) return "yellow";
        return "green";
    };

    const getWarning = () => {
        if (subject.skipped > max) return "THRESHOLD EXCEEDED";
        if (subject.skipped === max) return "LIMIT REACHED";
        if (perc >= 70) return "CRITICAL RISK";
        return "";
    };

    const color = getColorClass();
    const warn = getWarning();

    const formatTimestamp = (ts: number) => {
        return new Intl.DateTimeFormat('en-GB', {
            hour: '2-digit',
            minute: '2-digit',
            day: '2-digit',
            month: '2-digit'
        }).format(new Date(ts * 1000));
    };

    const handleSkip = async () => {
        const res = await fetch(`${API_URL}/skip/${subject.id}`, { method: "POST" });
        const data = await res.json();
        onSubjectsUpdate(data);
    };

    const handleUndo = async () => {
        const res = await fetch(`${API_URL}/undo/${subject.id}`, { method: "POST" });
        const data = await res.json();
        onSubjectsUpdate(data);
    };

    const handleDelete = async () => {
        if (window.confirm("Delete?")) {
            const res = await fetch(`${API_URL}/subjects/${subject.id}`, { method: "DELETE" });
            const data = await res.json();
            onSubjectsUpdate(data);
        }
    };

    return (
        <div className="bg-white dark:bg-gray-900 border border-blue-100 dark:border-gray-800 p-5 rounded-xl shadow-lg flex flex-col justify-between h-full gap-4">
            <div>
                <div className="flex justify-between items-start">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">{subject.name}</h2>
                    <button onClick={handleDelete} className="text-gray-500 hover:text-red-500 transition-colors" aria-label={`Delete ${subject.name}`}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                    </button>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">Missed: <span className="text-gray-900 dark:text-white font-bold">{subject.skipped}</span> / {max}</p>
                <div className="w-full bg-blue-50 dark:bg-gray-800 rounded-full h-2 mt-3 overflow-hidden" role="progressbar" aria-valuenow={Math.min(perc, 100)} aria-valuemin={0} aria-valuemax={100}>
                    <div className={`bg-${color}-500 h-full transition-all`} style={{ width: `${Math.min(perc, 100)}%` }}></div>
                </div>
                <p className={`text-[10px] font-bold text-${color}-500 mt-2`}>{warn}</p>
            </div>
            <div className="flex gap-2">
                <button onClick={handleSkip} className="flex-1 bg-blue-50 dark:bg-gray-800 py-2 rounded-lg text-sm font-bold border border-blue-200 dark:border-gray-700" aria-label={`Skip a class in ${subject.name}`}>+ Skip</button>
                <button
                    onClick={handleUndo}
                    disabled={subject.skipped === 0}
                    className="flex-1 text-gray-500 text-xs disabled:opacity-30 disabled:cursor-not-allowed"
                    aria-label={`Undo last skip in ${subject.name}`}
                >
                    Undo
                </button>
            </div>
            {subject.last_skipped && <p className="text-[10px] text-gray-500 mt-1">Last skipped: {formatTimestamp(subject.last_skipped)}</p>}
        </div>
    );
};

export default SubjectCard;
