import { create, StateCreator } from "zustand";

export interface EmailContact {
  id: string;
  email: string;
  name: string;
}

interface ApplicationState {
  emailInput: any;
  setEmailInput: any;
  nameInput: any;
  setNameInput: any;
  jobUrl: string;
  setJobUrl: (url: string) => void;
  jobDescription: string;
  setJobDescription: (desc: string) => void;
  resumeFile: File | null;
  setResumeFile: (file: File | null) => void;
  resumeText: string;
  setResumeText: (text: string) => void;
  emailList: EmailContact[];
  setEmailList: (list: EmailContact[]) => void;
  generatedSubject: string;
  setGeneratedSubject: (subject: string) => void;
  generatedTemplate: string;
  setGeneratedTemplate: (template: string) => void;
  reset: () => void;
  openaiKey: string;
  setOpenaiKey: (key: string) => void;
  credentials: string;
  setCredentials: (creds: string) => void;
  emailStats: { sent: number; successful: number; failed: number } | null;
  setEmailStats: (stats: { sent: number; successful: number; failed: number } | null) => void;
}

export const useApplicationStore = create<ApplicationState>((set) => ({
  jobUrl: "",
  setJobUrl: (jobUrl: string) => set({ jobUrl }),
  jobDescription: "",
  setJobDescription: (jobDescription: string) => set({ jobDescription }),
  resumeFile: null,
  setResumeFile: (resumeFile: File | null) => set({ resumeFile }),
  resumeText: "",
  setResumeText: (resumeText: string) => set({ resumeText }),
  emailInput: "",
  setEmailInput: (emailInput: string) => set({ emailInput }),
  nameInput: "",
  setNameInput: (nameInput: string) => set({ nameInput }),
  emailList: [],
  setEmailList: (emailList: EmailContact[]) => set({ emailList }),
  generatedSubject: "",
  setGeneratedSubject: (generatedSubject: string) => set({ generatedSubject }),
  generatedTemplate: "",
  setGeneratedTemplate: (generatedTemplate: string) => set({ generatedTemplate }),
  openaiKey: "",
  setOpenaiKey: (openaiKey: string) => set({ openaiKey }),
  credentials: "",
  setCredentials: (credentials: string) => set({ credentials }),
  emailStats: null,
  setEmailStats: (emailStats) => set({ emailStats }),
  reset: () => set({
    jobUrl: "",
    jobDescription: "",
    resumeFile: null,
    resumeText: "",
    emailInput: "",
    nameInput: "",
    emailList: [],
    generatedSubject: "",
    generatedTemplate: "",
    openaiKey: "",
    credentials: "",
    emailStats: null
  })
}));

