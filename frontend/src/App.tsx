import React, { useState, useEffect } from "react";
import type { Subject } from "./types";
import AddSubjectForm from "./components/AddSubjectForm";
import SubjectCard from "./components/SubjectCard";
import ChatWidget from "./components/ChatWidget";
import { API_URL } from "./config";

const App: React.FC = () => {
    const [subjects, setSubjects] = useState<Subject[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSubjects = async () => {
            try {
                const res = await fetch(`${API_URL}/subjects`);
                const data = await res.json();
                setSubjects(data);
            } catch (err) {
                console.error("Failed to fetch subjects:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchSubjects();
    }, []);

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-black text-gray-900 dark:text-gray-100 font-sans selection:bg-blue-100 dark:selection:bg-blue-900">
            <div className="max-w-6xl mx-auto px-4 py-8 sm:py-12">
                <header className="mb-12 flex flex-col sm:flex-row justify-between items-center gap-6">
                    <div className="text-center sm:text-left">
                        <h1 className="text-5xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-blue-400">NoMiss</h1>
                        <p className="text-gray-500 dark:text-gray-400 font-medium mt-2">Bagrut Attendance Optimizer</p>
                    </div>
                    <div className="flex bg-white dark:bg-gray-900 p-1.5 rounded-2xl shadow-sm border border-blue-50 dark:border-gray-800">
                        <div className="px-6 py-2 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-bold text-sm">Dashboard</div>
                    </div>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                    <div className="lg:col-span-2">
                        <AddSubjectForm onSubjectsUpdate={setSubjects} />

                        {loading ? (
                            <div className="flex justify-center py-20">
                                <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {subjects.length === 0 ? (
                                    <div className="col-span-full py-16 text-center bg-white dark:bg-gray-900 border-2 border-dashed border-blue-100 dark:border-gray-800 rounded-xl">
                                        <div className="text-4xl mb-4">📚</div>
                                        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-300">No subjects yet</h3>
                                        <p className="text-gray-500 mt-2">Add your subjects above to start optimizing your attendance.</p>
                                    </div>
                                ) : (
                                    subjects.map(sub => (
                                        <SubjectCard key={sub.id} subject={sub} onSubjectsUpdate={setSubjects} />
                                    ))
                                )}
                            </div>
                        )}
                    </div>

                    <div className="lg:col-span-1">
                        <div className="sticky top-8">
                            <ChatWidget />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default App;
