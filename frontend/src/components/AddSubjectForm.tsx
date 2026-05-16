import React, { useState } from "react";
import type { Subject } from "../types";
import { API_URL } from "../config";

interface AddSubjectFormProps {
    onSubjectsUpdate: (subjects: Subject[]) => void;
}

const AddSubjectForm: React.FC<AddSubjectFormProps> = ({ onSubjectsUpdate }) => {
    const [name, setName] = useState('');
    const [hours, setHours] = useState('');
    const [isAdding, setIsAdding] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name || !hours) return;

        setIsAdding(true);
        try {
            const res = await fetch(`${API_URL}/subjects`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: name,
                    totalHours: parseInt(hours),
                }),
            });
            const data = await res.json();
            setName('');
            setHours('');
            onSubjectsUpdate(data);
        } catch (err) {
            console.error("Failed to add subject:", err);
        } finally {
            setIsAdding(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 mb-10 bg-white dark:bg-gray-900 p-6 rounded-2xl shadow-xl border border-blue-100 dark:border-gray-800">
            <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Subject (e.g. Math)"
                className="flex-1 bg-blue-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                required
            />
            <input
                type="number"
                value={hours}
                onChange={(e) => setHours(e.target.value)}
                placeholder="Total Hours"
                className="w-full sm:w-32 bg-blue-50 dark:bg-gray-800 border-none rounded-xl px-4 py-3 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                required
            />
            <button
                type="submit"
                disabled={isAdding}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-xl shadow-lg shadow-blue-200 dark:shadow-none transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isAdding ? 'Adding...' : 'Add Subject'}
            </button>
        </form>
    );
};

export default AddSubjectForm;
