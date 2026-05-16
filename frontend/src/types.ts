export interface Subject {
    id: number;
    name: string;
    totalHours: number;
    skipped: number;
    last_skipped: number | null;
}

export interface ChatMessage {
    reply: string;
}
