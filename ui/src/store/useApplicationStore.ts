import { create, StateCreator } from "zustand";

export interface EmailContact {
  id: string;
  email: string;
  name: string;
  initials: string;
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
  generatedTemplate: string;
  setGeneratedTemplate: (template: string) => void;
  reset: () => void;
}

export const useApplicationStore = create<ApplicationState>((set: Parameters<StateCreator<ApplicationState>>[0]) => ({
  jobUrl: "https://techcorp.com/careers/senior-software-engineer",
  setJobUrl: (jobUrl: string) => set({ jobUrl }),
  jobDescription: "",
  setJobDescription: (jobDescription: string) => set({ jobDescription }),
  resumeFile: null,
  setResumeFile: (resumeFile: File | null) => set({ resumeFile }),
  resumeText: "",
  setResumeText: (resumeText: string) => set({ resumeText }),
  emailList: [],
  setEmailList: (emailList: EmailContact[]) => set({ emailList }),
  generatedTemplate: "",
  setGeneratedTemplate: (generatedTemplate: string) => set({ generatedTemplate }),
  reset: () => set({
    jobUrl: "https://techcorp.com/careers/senior-software-engineer",
    jobDescription: "",
    resumeFile: null,
    resumeText: "",
    emailList: [],
    generatedTemplate: ""
  })
})); 