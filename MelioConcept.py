import React, { useState, useRef, useEffect, useCallback } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, addDoc, query, onSnapshot, deleteDoc, getDocs, doc } from 'firebase/firestore';

// SettingsModal Component
const SettingsModal = ({
  show,
  onClose,
  currentBackground,
  onBackgroundChange,
  currentBlockColor,
  onBlockColorChange,
}) => {
  if (!show) return null;

  const backgroundOptions = [
    { name: "Purple to Blue", class: "from-purple-700 via-blue-600 to-indigo-700", value: "purple-blue-indigo" },
    { name: "Green to Teal", class: "from-green-400 to-teal-500", value: "green-teal" },
    { name: "Red to Orange", class: "from-red-500 to-orange-500", value: "red-orange" },
    { name: "Gray to Dark Gray", class: "from-gray-700 to-gray-900", value: "gray-darkgray" },
  ];

  const blockColorOptions = [
    { name: "Green to Teal", class: "from-green-300 to-teal-400", value: "green-teal" },
    { name: "Yellow to Orange", class: "from-yellow-300 to-orange-400", value: "yellow-orange" },
    { name: "Blue to Purple", class: "from-blue-300 to-purple-400", value: "blue-purple" }, // Corrected: changed '=' to ':'
    { name: "Pink to Red", class: "from-pink-300 to-red-400", value: "pink-red" },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg relative">
        <h2 className="text-3xl font-extrabold text-gray-800 mb-6 text-center">Personnalisation</h2>
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-3xl font-bold"
          aria-label="Fermer les paramètres"
        >
          &times;
        </button>

        {/* Background Customization */}
        <div className="mb-6">
          <label className="block text-xl font-semibold text-gray-700 mb-3">Couleur de Fond :</label>
          <div className="grid grid-cols-2 gap-4">
            {backgroundOptions.map(option => (
              <button
                key={option.value}
                onClick={() => onBackgroundChange(option.class)}
                className={`flex items-center justify-center p-3 rounded-lg border-2
                  ${currentBackground === option.class ? 'border-blue-500 ring-2 ring-blue-300' : 'border-gray-300'}
                  bg-gradient-to-br ${option.class} text-white font-medium hover:scale-105 transition-transform duration-200`}
              >
                {option.name}
              </button>
            ))}
          </div>
        </div>

        {/* Block Color Customization */}
        <div className="mb-6">
          <label className="block text-xl font-semibold text-gray-700 mb-3">Couleur des Blocs :</label>
          <div className="grid grid-cols-2 gap-4">
            {blockColorOptions.map(option => (
              <button
                key={option.value}
                onClick={() => onBlockColorChange(option.class)}
                className={`flex items-center justify-center p-3 rounded-lg border-2
                  ${currentBlockColor === option.class ? 'border-blue-500 ring-2 ring-blue-300' : 'border-gray-300'}
                  bg-gradient-to-br ${option.class} text-white font-medium hover:scale-105 transition-transform duration-200`}
              >
                {option.name}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={onClose}
          className="mt-8 w-full bg-indigo-600 text-white font-bold py-3 px-6 rounded-lg text-lg shadow-md hover:bg-indigo-700 transition duration-300 ease-in-out"
        >
          Fermer
        </button>
      </div>
    </div>
  );
};


// Main App component
function App() {
  // State for all draggable blocks on the canvas
  const [blocks, setBlocks] = useState([]);
  // State for the text currently being typed in the input bar
  const [newBlockText, setNewBlockText] = useState('');
  // State for displaying error messages to the user
  const [error, setError] = useState('');
  // State to store the ID of the block currently being dragged
  const [activeBlockId, setActiveBlockId] = useState(null);
  // Ref for the main canvas area to measure its dimensions and capture mouse events
  const canvasRef = useRef(null);
  // Store the initial mouse position relative to the block's top-left corner when dragging starts
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  // State to store all generated concepts for the collection (from Firestore)
  const [generatedConceptsCollection, setGeneratedConceptsCollection] = useState([]);

  // State for the deletion mode toggle
  const [isDeleteModeActive, setIsDeleteModeActive] = useState(false);

  // State for customization options
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [currentBackgroundClass, setCurrentBackgroundClass] = useState("from-purple-700 via-blue-600 to-indigo-700");
  const [currentBlockColorClass, setCurrentBlockColorClass] = useState("from-green-300 to-teal-400");

  // Firebase states
  const [db, setDb] = useState(null);
  const [auth, setAuth] = useState(null);
  const [userId, setUserId] = useState(null); // Authenticated user ID

  // Initialize Firebase and set up authentication
  useEffect(() => {
    // These global variables are provided by the Canvas environment
    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};

    const app = initializeApp(firebaseConfig);
    const firestore = getFirestore(app);
    const authInstance = getAuth(app);

    setDb(firestore);
    setAuth(authInstance);

    // Sign in anonymously or with custom token
    const unsubscribeAuth = onAuthStateChanged(authInstance, async (user) => {
      if (user) {
        setUserId(user.uid);
        console.log("Authenticated with Firebase:", user.uid);
      } else {
        try {
          if (typeof __initial_auth_token !== 'undefined') {
            await signInWithCustomToken(authInstance, __initial_auth_token);
            console.log("Attempted sign-in with custom token.");
          } else {
            const anonymousUser = await signInAnonymously(authInstance);
            setUserId(anonymousUser.user.uid);
            console.log("Signed in anonymously:", anonymousUser.user.uid);
          }
        } catch (error) {
          console.error("Firebase authentication error during custom token sign-in:", error);
          // If custom token fails, try anonymous sign-in as a fallback
          try {
            const anonymousUser = await signInAnonymously(authInstance);
            setUserId(anonymousUser.user.uid);
            console.log("Signed in anonymously after custom token failure:", anonymousUser.user.uid);
          } catch (anonError) {
            console.error("Firebase authentication error during anonymous sign-in:", anonError);
            setError("Erreur d'authentification Firebase. Veuillez réessayer ou contacter le support.");
          }
        }
      }
    });

    return () => unsubscribeAuth(); // Cleanup auth listener
  }, []); // Run once on component mount

  // Fetch concepts from Firestore when db and userId are available
  useEffect(() => {
    if (db && userId) {
      // Ensure __app_id is accessible here or passed as prop/context if not global
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      const conceptsCollectionRef = collection(db, `artifacts/${appId}/users/${userId}/concepts`);
      const q = query(conceptsCollectionRef);

      const unsubscribe = onSnapshot(q, (snapshot) => {
        const conceptsData = snapshot.docs.map(doc => doc.data().text);
        setGeneratedConceptsCollection(conceptsData);
        console.log("Concepts chargés depuis Firestore.");
      }, (error) => {
        console.error("Error fetching concepts from Firestore:", error);
        setError("Erreur lors du chargement des concepts.");
      });

      return () => unsubscribe(); // Cleanup snapshot listener
    }
  }, [db, userId]); // Re-run when db or userId changes

  // Function to add a new block to the canvas from the input bar
  const addBlock = () => {
    if (newBlockText.trim()) {
      const newId = crypto.randomUUID();
      const textContent = newBlockText.trim();
      const newBlock = {
        id: newId,
        text: textContent,
        x: Math.random() * (canvasRef.current.offsetWidth - 250) + 50,
        y: Math.random() * (canvasRef.current.offsetHeight - 100) + 50,
        isDragging: false,
        isGenerating: false,
        isNew: true,
        isExpanded: textContent.length <= 150,
      };
      setBlocks((prevBlocks) => [...prevBlocks, newBlock]);
      setNewBlockText('');
      setError('');
      setTimeout(() => {
        setBlocks(prevBlocks => prevBlocks.map(b => b.id === newId ? { ...b, isNew: false } : b));
      }, 500);
    } else {
      setError("Veuillez entrer du texte pour ajouter un bloc.");
    }
  };

  /**
   * Clears all blocks from the canvas AND from Firestore collection.
   * This function is triggered by the trash can icon button.
   */
  const clearAllBlocks = async () => {
    if (!db || !userId) {
      setError("Base de données non prête. Veuillez réessayer.");
      return;
    }
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      const conceptsCollectionRef = collection(db, `artifacts/${appId}/users/${userId}/concepts`);
      const snapshot = await getDocs(conceptsCollectionRef); // Get all documents
      // Delete each document
      snapshot.docs.forEach(async (document) => {
        await deleteDoc(doc(db, `artifacts/${appId}/users/${userId}/concepts`, document.id));
      });
      setBlocks([]); // Clear from canvas
      setError('');
      console.log("Tous les concepts ont été supprimés de Firestore.");
    } catch (err) {
      console.error("Error clearing all concepts from Firestore:", err);
      setError("Erreur lors de la suppression de tous les concepts.");
    }
  };

  /**
   * Toggles the delete mode on or off.
   * When active, clicking a block removes it from the canvas.
   */
  const toggleDeleteMode = () => {
    setIsDeleteModeActive(prevMode => !prevMode);
  };

  // Callback function to handle mouse down event on a block (start of drag or delete)
  const handleMouseDown = useCallback((e, id) => {
    e.preventDefault();

    if (isDeleteModeActive) {
      setBlocks(prevBlocks => prevBlocks.filter(b => b.id !== id));
      setError('');
    } else {
      const block = blocks.find(b => b.id === id);
      if (block) {
        setActiveBlockId(id);
        setDragOffset({
          x: e.clientX - block.x,
          y: e.clientY - block.y,
        });
        setBlocks(prevBlocks =>
          prevBlocks.map(b => (b.id === id ? { ...b, isDragging: true } : b))
        );
      }
    }
  }, [blocks, isDeleteModeActive]);

  // Callback function to handle mouse move event (during drag)
  const handleMouseMove = useCallback((e) => {
    if (activeBlockId === null || !canvasRef.current || isDeleteModeActive) return;

    let newX = e.clientX - dragOffset.x;
    let newY = e.clientY - dragOffset.y;

    const canvasRect = canvasRef.current.getBoundingClientRect();
    const currentBlock = blocks.find(b => b.id === activeBlockId);

    if (!currentBlock) return;

    const blockApproxWidth = 300;
    const blockApproxHeight = 100;

    newX = Math.max(0, Math.min(newX, canvasRect.width - blockApproxWidth));
    newY = Math.max(0, Math.min(newY, canvasRect.height - blockApproxHeight));

    setBlocks(prevBlocks =>
      prevBlocks.map(b =>
        b.id === activeBlockId
          ? { ...b, x: newX, y: newY }
          : b
      )
    );

    blocks.forEach(otherBlock => {
      if (otherBlock.id !== activeBlockId && !otherBlock.isDragging && !otherBlock.isGenerating) {
        const draggedBlock = blocks.find(b => b.id === activeBlockId);
        if (!draggedBlock) return;

        const areOverlapping =
          draggedBlock.x < otherBlock.x + blockApproxWidth * 0.7 &&
          draggedBlock.x + blockApproxWidth * 0.7 > otherBlock.x &&
          draggedBlock.y < otherBlock.y + blockApproxHeight * 0.7 &&
          draggedBlock.y + blockApproxHeight * 0.7 > otherBlock.y;

        if (areOverlapping) {
          combineBlocks(draggedBlock, otherBlock);
          setActiveBlockId(null);
          return;
        }
      }
    });

  }, [activeBlockId, dragOffset, blocks, isDeleteModeActive]);

  // Callback function to handle mouse up event (end of drag)
  const handleMouseUp = useCallback(() => {
    setBlocks(prevBlocks =>
      prevBlocks.map(b => (b.isDragging ? { ...b, isDragging: false } : b))
    );
    setActiveBlockId(null);
  }, []);

  // Effect hook to attach global mouse event listeners for drag functionality
  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  // Asynchronous function to combine two blocks and call the AI
  const combineBlocks = async (block1, block2) => {
    setError('');

    setBlocks(prevBlocks =>
      prevBlocks.filter(b => b.id !== block1.id && b.id !== block2.id)
    );

    const newConceptBlockId = crypto.randomUUID();
    const newConceptBlockPlaceholder = {
      id: newConceptBlockId,
      text: "Génération du concept...",
      x: (block1.x + block2.x) / 2,
      y: (block1.y + block2.y) / 2,
      isDragging: false,
      isGenerating: true,
      isNew: true,
      isExpanded: false,
    };
    setBlocks(prevBlocks => [...prevBlocks, newConceptBlockPlaceholder]);

    setTimeout(() => {
      setBlocks(prevBlocks => prevBlocks.map(b => b.id === newConceptBlockId ? { ...b, isNew: false } : b));
    }, 500);

    try {
      let prompt = '';
      const block1Lower = block1.text.toLowerCase();
      const block2Lower = block2.text.toLowerCase();

      const specificGameModes = ['bedwars', 'skywars', 'duels', 'hunger games', 'build battle', 'survival games', 'the walls'];

      let isSpecificGameModeInvolved = false;
      for (const mode of specificGameModes) {
        if (block1Lower.includes(mode) || block2Lower.includes(mode)) {
          isSpecificGameModeInvolved = true;
          break;
        }
      }

      if (isSpecificGameModeInvolved) {
        prompt = `En combinant "${block1.text}" et "${block2.text}", génère un SEUL défi vidéo créatif et captivant que l'on pourrait réaliser. Le défi doit être concret, mesurable, et inciter à une action spécifique en jeu. Ne commence pas la réponse par une introduction. Propose directement le défi. Exemple : Gagner une partie de Bedwars sans jamais acheter d'épée.`;
      } else {
        prompt = `En combinant "${block1.text}" et "${block2.text}", génère un SEUL concept vidéo unique et concret. Ne commence pas la réponse par une introduction. Propose directement l'idée de concept vidéo. Exemple : Série vidéo sur les mécanismes de construction avancés dans Minecraft, explorant des techniques de redstone complexes et des designs architecturaux innovants.`;
      }

      let chatHistory = [];
      chatHistory.push({ role: "user", parts: [{ text: prompt }] });

      const payload = { contents: chatHistory };
      const apiKey = "";
      const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur réseau: ${response.status} ${response.statusText} - ${errorText}`);
      }

      let result;
      try {
        result = await response.json();
      } catch (jsonError) {
        console.error("Erreur d'analyse JSON de la réponse:", jsonError);
        setBlocks(prevBlocks =>
          prevBlocks.map(b =>
            b.id === newConceptBlockId ? { ...b, text: "Erreur: Problème de parsing", isGenerating: false } : b
          )
        );
        setError("Réponse inattendue de l'IA. Veuillez réessayer. (Problème de parsing JSON)");
        return;
      }

      if (result.candidates && result.candidates.length > 0 &&
          result.candidates[0].content && result.candidates[0].content.parts &&
          result.candidates[0].content.parts.length > 0) {
        const text = result.candidates[0].content.parts[0].text;
        
        setBlocks(prevBlocks =>
          prevBlocks.map(b =>
            b.id === newConceptBlockId ? { ...b, text: text, isGenerating: false, isExpanded: text.length <= 150 } : b
          )
        );
        // Save the generated concept to Firestore
        if (db && userId) {
          try {
            const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
            const conceptsCollectionRef = collection(db, `artifacts/${appId}/users/${userId}/concepts`);
            await addDoc(conceptsCollectionRef, {
              text: text,
              timestamp: new Date(), // Add a timestamp for potential sorting
            });
            console.log("Concept ajouté à Firestore:", text);
          } catch (firestoreError) {
            console.error("Erreur lors de l'ajout du concept à Firestore:", firestoreError);
            setError("Erreur lors de la sauvegarde du concept.");
          }
        }

      } else {
        setError("Erreur lors de la génération du concept. La structure de la réponse de l'IA est inattendue.");
        setBlocks(prevBlocks =>
          prevBlocks.map(b =>
            b.id === newConceptBlockId ? { ...b, text: "Erreur: Concept non généré", isGenerating: false } : b
          )
        );
      }
    } catch (err) {
      setError("Une erreur est survenue lors de la communication avec l'IA. Vérifiez votre connexion.");
      setBlocks(prevBlocks =>
        prevBlocks.map(b =>
          b.id === newConceptBlockId ? { ...b, text: "Erreur de connexion!", isGenerating: false } : b
        )
      );
      console.error("Erreur lors de l'appel à l'API Gemini:", err);
    }
  };

  return (
    // Main container with full screen height and gradient background
    <div className={`min-h-screen bg-gradient-to-br ${currentBackgroundClass} flex flex-col font-sans relative overflow-hidden`}>
      {/* Header section */}
      <header className="p-6 bg-white bg-opacity-90 shadow-md rounded-b-xl mb-4 mx-4 mt-4 flex items-center justify-center z-10">
        <h1 className="text-4xl font-extrabold text-gray-800 tracking-tight text-center">
          MelioConcept
        </h1>
        {/* Settings Button */}
        <button
          onClick={() => {
            setShowSettingsModal(true);
          }}
          className="ml-4 p-2 rounded-full bg-gray-200 text-gray-600 hover:bg-gray-300 hover:text-gray-800 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-purple-300"
          aria-label="Ouvrir les paramètres de personnalisation"
        >
          <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37zM12 15.5a3.5 3.5 0 100-7 3.5 3.5 0 000 7z" />
          </svg>
        </button>
      </header>

      {/* Main interactive canvas area */}
      <div
        ref={canvasRef}
        className="flex-grow bg-white bg-opacity-70 rounded-xl shadow-inner m-4 relative overflow-hidden touch-action-none" // touch-action-none helps with touch devices
        style={{ minHeight: 'calc(100vh - 200px)' }} // Dynamically adjust height
      >
        {/* Render all the draggable blocks */}
        {blocks.map((block) => (
          <div
            key={block.id}
            // Dynamic classes for styling based on dragging and generating states
            className={`absolute p-4 rounded-lg shadow-lg cursor-grab select-none transform transition-transform duration-100 ease-out active:cursor-grabbing max-w-md
                      ${block.isDragging ? 'z-50 scale-105 shadow-2xl ring-4 ring-blue-400' : 'z-auto'}
                      ${block.isGenerating ? 'bg-gray-200 text-gray-500 animate-pulse' : `bg-gradient-to-br ${currentBlockColorClass} text-gray-800`}
                      ${block.isNew ? 'animate-scaleIn' : ''}
                      ${isDeleteModeActive ? 'cursor-pointer border-2 border-red-500 ring-2 ring-red-300' : ''} {/* Visual feedback for delete mode */}
                      flex flex-col justify-between`}
            // Position blocks using inline styles
            style={{ left: block.x, top: block.y }}
            // Attach mouse down event to start dragging or trigger deletion
            onMouseDown={(e) => handleMouseDown(e, block.id)}
            role="button"
            tabIndex="0"
            aria-label={`Bloc de concept: ${block.text}`}
          >
            {/* Display block text, allow wrapping, and show spinner if generating */}
            <p className={`font-semibold text-lg whitespace-pre-wrap flex items-center ${block.isExpanded ? 'expanded-text' : 'truncated-text'}`}>
              {block.isGenerating && (
                <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.03 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              )}
              {block.text}
            </p>
            {/* Show "Voir plus/moins" button only if not generating and text is long enough */}
            {!block.isGenerating && block.text.length > 150 && (
              <button
                onClick={(e) => { // Prevent event bubbling to parent for drag/delete
                  e.stopPropagation();
                  setBlocks(prevBlocks => prevBlocks.map(b => b.id === block.id ? { ...b, isExpanded: !b.isExpanded } : b));
                }}
                className="mt-2 text-sm text-blue-800 hover:text-blue-600 font-bold self-end focus:outline-none focus:ring-2 focus:ring-blue-300 rounded-md"
              >
                {block.isExpanded ? 'Voir moins' : 'Voir plus'}
              </button>
            )}
          </div>
        ))}

        {/* Error message overlay */}
        {error && (
          <div className="absolute inset-0 bg-red-100 bg-opacity-80 flex items-center justify-center rounded-xl z-40">
            <div className="bg-white p-6 rounded-lg shadow-xl flex flex-col items-center">
              <p className="text-red-700 font-bold text-lg text-center mb-2">Erreur :</p>
              <p className="text-red-600 text-base text-center">{error}</p>
              <button
                onClick={() => setError('')}
                className="mt-4 bg-red-500 text-white py-2 px-4 rounded-lg hover:bg-red-600 transition duration-200"
              >
                Fermer
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Input bar at the bottom for adding new blocks and trash button */}
      <div className="p-4 bg-white bg-opacity-90 shadow-lg rounded-t-xl mt-4 mx-4 flex flex-col sm:flex-row items-center justify-center gap-4 z-10">
        <input
          type="text"
          className="flex-grow w-full sm:w-auto p-3 border-2 border-purple-300 rounded-lg focus:ring-4 focus:ring-purple-200 focus:border-purple-500 transition duration-200 text-lg placeholder-gray-400"
          placeholder="Ajouter un nouveau concept (ex: Espace)"
          value={newBlockText}
          onChange={(e) => setNewBlockText(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') addBlock(); // Add block on Enter key press
          }}
          aria-label="Ajouter un nouveau concept"
        />
        <button
          onClick={addBlock}
          className="w-full sm:w-auto bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold py-3 px-6 rounded-lg text-lg shadow-md hover:from-indigo-600 hover:to-purple-700 transition duration-300 ease-in-out transform hover:-translate-y-0.5 hover:scale-105 disabled:opacity-60 disabled:cursor-not-allowed"
          disabled={!newBlockText.trim()} // Disable button if input is empty
          aria-label="Ajouter un bloc"
        >
          Ajouter Bloc
        </button>

        {/* Trash all blocks button */}
        <button
          onClick={clearAllBlocks}
          className="w-full sm:w-auto bg-red-500 text-white font-bold py-3 px-6 rounded-lg text-lg shadow-md hover:bg-red-600 transition duration-300 ease-in-out transform hover:-translate-y-0.5 hover:scale-105 flex items-center justify-center"
          aria-label="Supprimer tous les blocs"
        >
          <svg className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Tout supprimer
        </button>

        {/* Toggle Delete Mode Button */}
        <button
          onClick={toggleDeleteMode}
          className={`w-full sm:w-auto font-bold py-3 px-6 rounded-lg text-lg shadow-md transition duration-300 ease-in-out transform hover:-translate-y-0.5 hover:scale-105 flex items-center justify-center
                      ${isDeleteModeActive ? 'bg-red-600 text-white' : 'bg-gray-300 text-gray-800 hover:bg-gray-400'}`}
          aria-pressed={isDeleteModeActive}
          aria-label="Activer/Désactiver le mode suppression de bloc"
        >
          <svg className={`h-6 w-6 mr-2 ${isDeleteModeActive ? 'text-white' : 'text-gray-600'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          {isDeleteModeActive ? 'Mode Suppression: Actif' : 'Mode Suppression: Inactif'}
        </button>
      </div>

      {/* Collection Section */}
      {generatedConceptsCollection.length > 0 && (
        <div className="bg-white bg-opacity-90 rounded-xl shadow-lg p-6 m-4 mt-0">
          <h2 className="text-3xl font-extrabold text-gray-800 mb-6 text-center">
            Collection de Concepts
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {generatedConceptsCollection.map((concept, index) => (
              <div key={index} className="bg-gray-50 p-5 rounded-lg shadow-inner border border-gray-200">
                <p className="text-gray-800 leading-relaxed text-base whitespace-pre-wrap">{concept}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tailwind CSS Custom Animation Definition */}
      <style>
        {`
        @keyframes scaleIn {
          from {
            opacity: 0;
            transform: scale(0.8);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        .animate-scaleIn {
          animation: scaleIn 0.5s ease-out forwards;
        }

        .truncated-text {
          max-height: 6em; /* Adjust this value as needed for the desired number of lines */
          overflow: hidden;
          display: -webkit-box;
          -webkit-line-clamp: 3; /* Limit to 3 lines for truncation */
          -webkit-box-orient: vertical;
        }
        .expanded-text {
          max-height: none;
          overflow: visible;
        }
        `}
      </style>

      {/* Settings Modal */}
      <SettingsModal
        show={showSettingsModal}
        onClose={() => setShowSettingsModal(false)}
        currentBackground={currentBackgroundClass}
        onBackgroundChange={setCurrentBackgroundClass}
        currentBlockColor={currentBlockColorClass}
        onBlockColorChange={setCurrentBlockColorClass}
      />
    </div>
  );
}

export default App;
