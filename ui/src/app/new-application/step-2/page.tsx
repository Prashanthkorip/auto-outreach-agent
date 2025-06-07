"use client";
import { useRouter } from "next/navigation";
import { useApplicationStore } from "@/store/useApplicationStore";
import { X, User, Plus, Eye, Edit, Bold, Italic, List, ListOrdered, Link, Code, Quote, ArrowLeft, ArrowRight } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

export default function Step2Page() {
  const router = useRouter();
  const {
    emailList, setEmailList,
    generatedTemplate, setGeneratedTemplate,
    generatedSubject, setGeneratedSubject,
    setEmailStats
  } = useApplicationStore();

  const isComplete = emailList.length > 0;

  const onCancel = () => {
    router.push("/new-application/step-1");
  };
  const [isSending, setIsSending] = useState(false);

  const onNext = async () => {
    setIsSending(true);
    try {
      const resp = await fetch("http://0.0.0.0:8000/send-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          recipients: emailList,
          subject: generatedSubject,
          content: generatedTemplate
        })
      });
      const data = await resp.json();
      if (typeof data.sent === "number" && typeof data.successful === "number" && typeof data.failed === "number") {
        setEmailStats({ sent: data.sent, successful: data.successful, failed: data.failed });
        router.push("/new-application/step-3");
      } else {
        alert("Failed to send emails. Please try again.");
      }
    } catch (e) {
      alert("Error sending emails.");
    } finally {
      setIsSending(false);
    }
  };

  const [isPreviewMode, setIsPreviewMode] = useState(true);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Format text functions
    const insertFormat = (prefix: string, suffix: string = '', placeholder: string = 'text') => {
        if (!textareaRef.current) return;

        const textarea = textareaRef.current;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);
        const textToInsert = selectedText || placeholder;
        const newText = prefix + textToInsert + suffix;

        const newValue = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
        setGeneratedTemplate(newValue);

        // Set cursor position
        setTimeout(() => {
            textarea.focus();
            if (selectedText) {
                textarea.setSelectionRange(start + prefix.length, start + prefix.length + selectedText.length);
            } else {
                textarea.setSelectionRange(start + prefix.length, start + prefix.length + placeholder.length);
            }
        }, 0);
    };

    const formatBold = () => insertFormat('**', '**', 'bold text');
    const formatItalic = () => insertFormat('*', '*', 'italic text');
    const formatBulletList = () => insertFormat('\n- ', '', 'list item');
    const formatNumberedList = () => insertFormat('\n1. ', '', 'list item');
    const formatCode = () => insertFormat('`', '`', 'code');
    const formatQuote = () => insertFormat('\n> ', '', 'quote');
    const formatLink = () => insertFormat('[', '](url)', 'link text');

    // Helper to update a recipient
    const updateRecipient = (id: string, field: 'name' | 'email', value: string) => {
        const updated = emailList.map((contact) =>
            contact.id === id ? { ...contact, [field]: value } : contact
        );
        setEmailList(updated);
    };

    // Helper to add a new recipient
    const [newName, setNewName] = useState('');
    const [newEmail, setNewEmail] = useState('');
    const getInitials = (name: string) => name.split(' ').map(w => w[0]?.toUpperCase() || '').join('').slice(0, 2);
    const addNewRecipient = () => {
        if (!newEmail.trim()) return;
        if (emailList.some(c => c.email === newEmail.trim().toLowerCase())) return;
        const name = newName.trim() || newEmail.split('@')[0];
        setEmailList([
            ...emailList,
            {
                id: Date.now().toString(),
                email: newEmail.trim().toLowerCase(),
                name,
            }
        ]);
        setNewName('');
        setNewEmail('');
    };

    useEffect(() => {
        // Fetch generated email subject, content, and recipients on mount
        Promise.all([
            fetch("http://0.0.0.0:8000/get-generated-email").then(res => res.json()),
            fetch("http://0.0.0.0:8000/get-recipients").then(res => res.json())
        ]).then(([emailData, recipientsData]) => {
            if (emailData.subject) setGeneratedSubject(emailData.subject);
            if (emailData.content) setGeneratedTemplate(emailData.content);
            if (Array.isArray(recipientsData.recipients)) setEmailList(recipientsData.recipients);
        });
    }, [setGeneratedSubject, setGeneratedTemplate, setEmailList]);

      // Debounce helpers
  function useDebouncedEffect(effect: () => void, deps: any[], delay: number) {
    const callback = useRef<ReturnType<typeof setTimeout> | null>(null);
    useEffect(() => {
      if (callback.current) clearTimeout(callback.current);
      callback.current = setTimeout(effect, delay);
      return () => {
        if (callback.current) clearTimeout(callback.current);
      };
    }, deps);
  }

  useDebouncedEffect(() => {
    if (emailList) {
      fetch("http://0.0.0.0:8000/save-recipients", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ recipients: emailList })
      });
    }
  }, [emailList], 1000);

  useDebouncedEffect(() => {
    if (emailList) {
      fetch("http://0.0.0.0:8000/save-generated-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject: generatedSubject, content: generatedTemplate })
      });
    }
  }, [generatedSubject, generatedTemplate], 1000);

    return (
        <div className="w-full max-h-[calc(100vh-64px)] h-screen flex-shrink-0 flex flex-col overflow-hidden">
            <div className="flex-1 flex flex-col p-6 max-h-full h-full overflow-hidden">
                <div className="w-full flex flex-row gap-8 max-h-full h-full flex-1 overflow-hidden">
                    {/* Left Panel: Recipients */}
                    <div className="w-2/5 bg-white rounded-lg border border-gray-200 p-6 flex flex-col h-full max-h-full overflow-hidden">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recipients ({emailList.length})</h3>
                        <div className="flex flex-col gap-3 max-h-full overflow-y-auto">
                            {emailList.map((contact) => (
                                <div key={contact.id} className="flex items-center gap-3 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
                                    {/* Avatar */}
                                    <div className="w-12 h-12 min-w-12 min-h-12 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-base">
                                        {getInitials(contact.name)}
                                    </div>
                                    {/* Editable Name and Email stacked */}
                                    <div className="flex flex-col flex-1 min-w-0">
                                        <input
                                            type="text"
                                            value={contact.name}
                                            onChange={e => updateRecipient(contact.id, 'name', e.target.value)}
                                            className="font-semibold text-gray-900 bg-transparent border-none outline-none px-0 text-base focus:bg-blue-50 rounded truncate"
                                            placeholder="Name"
                                        />
                                        <input
                                            type="email"
                                            value={contact.email}
                                            onChange={e => updateRecipient(contact.id, 'email', e.target.value)}
                                            className="text-gray-700 bg-transparent border-none outline-none px-0 text-base focus:bg-blue-50 rounded truncate"
                                            placeholder="Email"
                                        />
                                    </div>
                                    <button
                                        onClick={() => setEmailList(emailList.filter(c => c.id !== contact.id))}
                                        className="ml-auto text-gray-400 hover:text-red-500"
                                        title="Remove"
                                    >
                                        <X className="w-4 h-4" />
                                    </button>
                                </div>
                            ))}

                        </div>
                        {/* Add new recipient row */}
                        <div className="text-gray-800 mt-5 mb-2">New Recipient</div>
                        <div className="flex items-center gap-3 bg-gray-50 border border-dashed border-gray-300 rounded-lg px-3 py-2">
                            <div className="w-12 h-12 min-w-12 min-h-12 rounded-full bg-gray-200 flex items-center justify-center text-gray-400 font-bold text-base">
                                <User className="w-5 h-5" />
                            </div>
                            <div className="flex flex-col flex-1 min-w-0">
                                <input
                                    type="text"
                                    value={newName}
                                    onChange={e => setNewName(e.target.value)}
                                    className="font-medium text-gray-900 bg-transparent border-none outline-none px-0 focus:bg-blue-50 rounded"
                                    placeholder="Name"
                                    onKeyDown={e => { if (e.key === 'Enter') addNewRecipient(); }}
                                />
                                <input
                                    type="email"
                                    value={newEmail}
                                    onChange={e => setNewEmail(e.target.value)}
                                    className="text-gray-700 bg-transparent border-none outline-none px-0 focus:bg-blue-50 rounded"
                                    placeholder="Email"
                                    onKeyDown={e => { if (e.key === 'Enter') addNewRecipient(); }}
                                    onBlur={addNewRecipient}
                                />
                            </div>

                            <button
                                onClick={addNewRecipient}
                                className="ml-auto text-gray-400 hover:text-blue-600"
                                title="Add"
                            >
                                <Plus className="w-4 h-4" />
                            </button>
                        </div>
                        <div className="mt-4 text-sm text-gray-500">{emailList.length} recipient{emailList.length !== 1 ? 's' : ''}</div>
                    </div>

                    {/* Right Panel: Email Editor (existing) */}
                    <div className="w-3/5 flex flex-col max-h-full overflow-hidden">
                        <div className="w-full flex flex-col max-h-full h-full">

                            {/* Email Composer */}
                            <div className="flex-1 bg-white rounded-lg border border-gray-200 p-6 flex flex-col max-h-full overflow-hidden">

                                {/* Subject Line */}
                                <div className="mb-4">
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Subject
                                    </label>
                                    <input
                                        type="text"
                                        value={generatedSubject}
                                        onChange={e => setGeneratedSubject(e.target.value)}
                                        className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md text-gray-900 focus:outline-none"
                                    />
                                </div>

                                {/* Email Content */}
                                <div className="flex-1 mb-4 max-h-full h-full overflow-hidden flex flex-col">
                                    <div className="flex items-center justify-between mb-2">
                                        <label className="block text-sm font-medium text-gray-700">
                                            Email Content
                                        </label>
                                        <div className="flex items-center gap-2">
                                            <button
                                                onClick={() => setIsPreviewMode(true)}
                                                className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${isPreviewMode
                                                    ? 'bg-blue-100 text-blue-700'
                                                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                                    }`}
                                            >
                                                <Eye className="w-3 h-3 mr-1 inline" />
                                                Preview
                                            </button>
                                            <button
                                                onClick={() => setIsPreviewMode(false)}
                                                className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${!isPreviewMode
                                                    ? 'bg-blue-100 text-blue-700'
                                                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                                    }`}
                                            >
                                                <Edit className="w-3 h-3 mr-1 inline" />
                                                Edit
                                            </button>
                                        </div>
                                    </div>

                                    <div className="flex-1 border border-gray-300 rounded-md max-h-full overflow-hidden h-full">
                                        {!isPreviewMode ? (
                                            // Edit Mode
                                            <div className="flex flex-col h-full">
                                                {/* Toolbar */}
                                                <div className="border-b border-gray-200 bg-gray-50 px-3 py-2">
                                                    <div className="flex items-center gap-1">
                                                        <button
                                                            onClick={formatBold}
                                                            className="p-2 text-gray-600 hover:bg-gray-200 rounded transition-colors"
                                                            title="Bold (Ctrl+B)"
                                                        >
                                                            <Bold className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            onClick={formatItalic}
                                                            className="p-2 text-gray-600 hover:bg-gray-200 rounded transition-colors"
                                                            title="Italic (Ctrl+I)"
                                                        >
                                                            <Italic className="w-4 h-4" />
                                                        </button>
                                                        <div className="w-px h-6 bg-gray-300 mx-1"></div>
                                                        <button
                                                            onClick={formatBulletList}
                                                            className="p-2 text-gray-600 hover:bg-gray-200 rounded transition-colors"
                                                            title="Bullet List"
                                                        >
                                                            <List className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            onClick={formatNumberedList}
                                                            className="p-2 text-gray-600 hover:bg-gray-200 rounded transition-colors"
                                                            title="Numbered List"
                                                        >
                                                            <ListOrdered className="w-4 h-4" />
                                                        </button>
                                                        <div className="w-px h-6 bg-gray-300 mx-1"></div>
                                                        <button
                                                            onClick={formatLink}
                                                            className="p-2 text-gray-600 hover:bg-gray-200 rounded transition-colors"
                                                            title="Insert Link"
                                                        >
                                                            <Link className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            onClick={formatCode}
                                                            className="p-2 text-gray-600 hover:bg-gray-200 rounded transition-colors"
                                                            title="Code"
                                                        >
                                                            <Code className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            onClick={formatQuote}
                                                            className="p-2 text-gray-600 hover:bg-gray-200 rounded transition-colors"
                                                            title="Quote"
                                                        >
                                                            <Quote className="w-4 h-4" />
                                                        </button>
                                                    </div>
                                                </div>

                                                {/* Text Editor */}
                                                <textarea
                                                    ref={textareaRef}
                                                    value={generatedTemplate}
                                                    onChange={(e) => setGeneratedTemplate(e.target.value)}
                                                    placeholder="Compose your email here..."
                                                    className="flex-1 p-4 text-gray-900 bg-white resize-none focus:outline-none h-full"
                                                    style={{ fontFamily: 'inherit' }}
                                                />
                                            </div>
                                        ) : (
                                            // Preview Mode
                                            <div className="p-4 bg-white overflow-y-auto min-h-[400px] h-full">
                                                <div className="max-w-none text-gray-900">
                                                    <ReactMarkdown
                                                        components={{
                                                            h1: ({ node, ...props }) => <h1 className="text-xl font-bold mb-3 text-gray-900" {...props} />,
                                                            h2: ({ node, ...props }) => <h2 className="text-lg font-semibold mb-2 mt-4 text-gray-900" {...props} />,
                                                            h3: ({ node, ...props }) => <h3 className="text-base font-medium mb-2 mt-3 text-gray-900" {...props} />,
                                                            p: ({ node, ...props }) => <p className="mb-3 text-gray-700 leading-relaxed" {...props} />,
                                                            ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-3 space-y-1" {...props} />,
                                                            ol: ({ node, ...props }) => <ol className="list-decimal list-inside mb-3 space-y-1" {...props} />,
                                                            li: ({ node, ...props }) => <li className="text-gray-700" {...props} />,
                                                            strong: ({ node, ...props }) => <strong className="font-semibold text-gray-900" {...props} />,
                                                            em: ({ node, ...props }) => <em className="italic text-gray-700" {...props} />,
                                                            code: ({ node, ...props }) => <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono text-gray-900" {...props} />,
                                                            a: ({ node, ...props }) => <a className="text-blue-600 hover:underline" {...props} />,
                                                            hr: ({ node, ...props }) => <hr className="my-4 border-gray-300" {...props} />,
                                                        }}
                                                    >
                                                        {generatedTemplate || '*No content to preview*'}
                                                    </ReactMarkdown>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Continue Button */}
                <div className="mt-4 flex justify-between">
                    <button
                        onClick={onCancel}
                        className={`px-6 py-3 font-semibold rounded-lg transition-colors bg-gray-100 text-gray-900 border border-gray-200`}
                    >
                        <ArrowLeft className="w-6 h-6 mr-2 inline mb-0.5" />
                        Back
                    </button>
                    <button
                        onClick={onNext}
                        disabled={!isComplete || isSending}
                        className={`px-6 py-3 font-semibold rounded-lg transition-colors ${isComplete && !isSending
                            ? 'bg-blue-600 hover:bg-blue-700 text-white'
                            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }`}
                    >
                        {isSending ? 'Sending...' : 'Send Emails'}
                        <ArrowRight className="w-6 h-6 ml-2 inline mb-0.5" />
                    </button>
                </div>
            </div>
        </div>
    );
} 