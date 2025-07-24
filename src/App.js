import React, { useState, useEffect } from 'react';

function App() {
    const [prompt, setPrompt] = useState('');
    const [generatedText, setGeneratedText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    // Function to call the Gemini API for text generation
    const generateContent = async () => {
        setIsLoading(true);
        setError('');
        setGeneratedText('');

        try {
            let chatHistory = [];
            chatHistory.push({ role: "user", parts: [{ text: prompt }] });

            const payload = { contents: chatHistory };
            const apiKey = ""; // Leave this as-is; Canvas provides the key at runtime.
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error?.message || 'Failed to generate content.');
            }

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const text = result.candidates[0].content.parts[0].text;
                setGeneratedText(text);
            } else {
                setError('No content generated. Please try again.');
            }
        } catch (err) {
            console.error("Error generating content:", err);
            setError(`Error: ${err.message || 'Something went wrong.'}`);
        } finally {
            setIsLoading(false);
        }
    };

    // Handle Enter key press
    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !isLoading && prompt.trim() !== '') {
            generateContent();
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 text-gray-100 font-sans flex flex-col items-center justify-center p-4">
            <header className="text-center mb-8">
                <h1 className="text-5xl font-extrabold text-blue-400 mb-2">MelioConcept AI</h1>
                <p className="text-xl text-gray-300">Générez du texte avec l'IA</p>
            </header>

            <main className="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-2xl">
                <div className="mb-6">
                    <label htmlFor="prompt-input" className="block text-lg font-medium text-gray-200 mb-2">
                        Votre requête pour l'IA :
                    </label>
                    <textarea
                        id="prompt-input"
                        className="w-full p-4 rounded-lg bg-gray-700 text-gray-100 border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200 resize-y min-h-[100px]"
                        placeholder="Ex: Écrivez une courte histoire sur un robot explorant une nouvelle planète..."
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={isLoading}
                    ></textarea>
                </div>

                <button
                    onClick={generateContent}
                    disabled={isLoading || prompt.trim() === ''}
                    className={`w-full py-3 px-6 rounded-lg font-bold text-lg transition-all duration-300
                        ${isLoading || prompt.trim() === ''
                            ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg transform hover:scale-105'
                        }`}
                >
                    {isLoading ? (
                        <span className="flex items-center justify-center">
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Génération en cours...
                        </span>
                    ) : (
                        'Générer le texte'
                    )}
                </button>

                {error && (
                    <div className="mt-6 p-4 bg-red-800 text-red-100 rounded-lg shadow-md">
                        <p className="font-bold">Erreur :</p>
                        <p>{error}</p>
                    </div>
                )}

                {generatedText && (
                    <div className="mt-6 p-6 bg-gray-700 rounded-lg shadow-inner border border-gray-600">
                        <h2 className="text-xl font-semibold text-blue-300 mb-3">Texte généré :</h2>
                        <p className="text-gray-200 whitespace-pre-wrap">{generatedText}</p>
                    </div>
                )}
            </main>

            <footer className="mt-8 text-gray-400 text-sm text-center">
                <p>&copy; {new Date().getFullYear()} MelioConcept AI. Tous droits réservés.</p>
            </footer>
        </div>
    );
}

export default App;