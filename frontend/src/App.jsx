import { useEffect, useState } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import KnowledgeGraph from "./KnowledgeGraph";

// function OldApp() {
//   const [hierarchy, setHierarchy] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState("");
//   const [selectedFiles, setSelectedFiles] = useState([]);
//   const [uploading, setUploading] = useState(false);
//   const [uploadMessage, setUploadMessage] = useState("");
//   // Stores which topics are expanded
//   const [expandedTopics, setExpandedTopics] = useState({});
//   // Stores the currently selected subtopic
//   const [selectedSubtopic, setSelectedSubtopic] = useState(null);
//   const [question, setQuestion] = useState("");
//   const [answer, setAnswer] = useState("");
//   const [asking, setAsking] = useState(false);
//   const [globalAI, setGlobalAI] = useState(false);
//   const [globalQuestion, setGlobalQuestion] = useState("");
//   const [globalAnswer, setGlobalAnswer] = useState("");
//   const [globalAsking, setGlobalAsking] = useState(false);
//   const [videoFile, setVideoFile] = useState(null);
//   const [videoUploading, setVideoUploading] = useState(false);
//   const [videoMessage, setVideoMessage] = useState("");
//   const [selectedCourse, setSelectedCourse] = useState("");
  

//   useEffect(() => {
//     fetch("http://127.0.0.1:8000/hierarchy")
//       .then((response) => {
//         if (!response.ok) {
//           throw new Error("Failed to fetch hierarchy");
//         }

//         return response.json();
//       })
//       .then((data) => {
//         setHierarchy(data);
//         setLoading(false);
//       })
//       .catch((error) => {
//         console.error(error);
//         setError("Could not connect to the backend.");
//         setLoading(false);
//       });
//   }, []);

//   const handleUpload = async () => {
//     if (selectedFiles.length === 0) {
//       setUploadMessage("Please select at least one file.");
//       return;
//     }

//     setUploading(true);
//     setUploadMessage("");

//     const formData = new FormData();

//     selectedFiles.forEach((file) => {
//       formData.append("files", file);
//     });

//     try {
//       const response = await fetch("http://127.0.0.1:8000/upload", {
//         method: "POST",
//         body: formData,
//       });

//       if (!response.ok) {
//         throw new Error("Upload failed");
//       }

//       await response.json();

//       setUploadMessage("✅ Files uploaded successfully!");

//       // Refresh hierarchy
//       const hierarchyResponse = await fetch(
//         "http://127.0.0.1:8000/hierarchy"
//       );

//       const updatedHierarchy = await hierarchyResponse.json();

//       setHierarchy(updatedHierarchy);

//       setSelectedFiles([]);

//     } catch (error) {
//       console.error(error);
//       setUploadMessage("❌ Upload failed. Please try again.");
//     }

//     setUploading(false);
//   };

//   const handleVideoUpload = async () => {
//     if (!videoFile) {
//       setVideoMessage("Please select a video first.");
//       return;
//     }

//     setVideoUploading(true);
//     setVideoMessage("");

//     const formData = new FormData();
//     formData.append("file", videoFile);

//     try {
//       const response = await fetch(
//         "http://127.0.0.1:8000/upload-video",
//         {
//           method: "POST",
//           body: formData,
//         }
//       );

//       if (!response.ok) {
//         throw new Error("Video upload failed");
//       }

//       await response.json();

//       setVideoMessage(
//         "✅ Lecture processed successfully!"
//       );

//       // Refresh hierarchy
//       const hierarchyResponse = await fetch(
//         "http://127.0.0.1:8000/hierarchy"
//       );

//       const updatedHierarchy = await hierarchyResponse.json();

//       setHierarchy(updatedHierarchy);

//       setVideoFile(null);

//     } catch (error) {
//       console.error(error);
//       setVideoMessage(
//         "❌ Video processing failed. Please try again."
//       );
//     } finally {
//       setVideoUploading(false);
//     }
//   };

//   const askAI = async () => {
//     if (!question.trim()) return;

//     setAsking(true);
//     setAnswer("");

//     try {
//       const response = await fetch("http://127.0.0.1:8000/ask", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({
//         question: question,
//         topic: selectedSubtopic.topicName,
//         subtopic: selectedSubtopic.name,
//         document: selectedSubtopic.documentTitle,
//       }),
//       });

//       if (!response.ok) {
//         throw new Error("Failed to get AI response");
//       }

//       const data = await response.json();

//       setAnswer(data.answer);
//     } catch (error) {
//       console.error(error);
//       setAnswer("Something went wrong while asking the AI.");
//     } finally {
//       setAsking(false);
//     }
//   };

//   const askGlobalAI = async () => {
//     if (!globalQuestion.trim()) return;

//     setGlobalAsking(true);
//     setGlobalAnswer("");

//     try {
//       const response = await fetch("http://127.0.0.1:8000/ask", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({
//           question: globalQuestion,
//         }),
//       });

//       if (!response.ok) {
//         throw new Error("Failed to get AI response");
//       }

//       const data = await response.json();

//       setGlobalAnswer(data.answer);
//     } catch (error) {
//       console.error(error);
//       setGlobalAnswer(
//         "Something went wrong while asking the AI."
//       );
//     } finally {
//       setGlobalAsking(false);
//     }
//   };

//   // Expand / collapse a topic
//   const toggleTopic = (documentId, topicId) => {
//     const key = `${documentId}-${topicId}`;

//     setExpandedTopics((previous) => ({
//       ...previous,
//       [key]: !previous[key],
//     }));
//   };

//   // Loading state
//   if (loading) {
//     return (
//       <div className="app">
//         <h1>AI Education</h1>
//         <p>Loading knowledge tree...</p>
//       </div>
//     );
//   }

//   // Error state
//   if (error) {
//     return (
//       <div className="app">
//         <h1>AI Education</h1>
//         <p className="error">{error}</p>
//       </div>
//     );
//   }

//   return (
//     <div className="app">

//       <header>
//         <h1>AI Education</h1>
//         <br></br>
//         <p>Interactive Knowledge Tree</p>
//       </header>

//       <div className="upload-section">

//         <h2>📤 Add Study Material</h2>

//         <p>
//           Upload PDF or PowerPoint files to build your knowledge tree.
//         </p>

//         <input
//           type="file"
//           accept=".pdf,.pptx"
//           multiple
//           onChange={(event) =>
//             setSelectedFiles(Array.from(event.target.files))
//           }
//         />

//         {selectedFiles.length > 0 && (
//           <div className="selected-files">
//             {selectedFiles.map((file) => (
//               <div key={file.name}>
//                 📄 {file.name}
//               </div>
//             ))}
//           </div>
//         )}

//         <button
//           className="upload-button"
//           onClick={handleUpload}
//           disabled={uploading}
//         >
//           {uploading
//             ? "Processing..."
//             : "Upload & Build Knowledge Tree"}
//         </button>

//         {uploadMessage && (
//           <p className="upload-message">
//             {uploadMessage}
//           </p>
//         )}
//       </div>

//       <div className="upload-section video-upload-section">

//         <h2>🎥 Add Lecture Video</h2>

//         <p>
//           Upload a lecture video to generate topics, subtopics,
//           and make the lecture searchable by AI.
//         </p>

//         <input
//           type="file"
//           accept="video/*"
//           onChange={(event) => {
//             setVideoFile(event.target.files[0] || null);
//             setVideoMessage("");
//           }}
//         />

//         {videoFile && (
//           <div className="selected-files">
//             🎥 {videoFile.name}
//           </div>
//         )}

//         <button
//           className="upload-button"
//           onClick={handleVideoUpload}
//           disabled={videoUploading || !videoFile}
//         >
//           {videoUploading
//             ? "🎥 Processing Lecture..."
//             : "Upload & Process Lecture"}
//         </button>

//         {videoMessage && (
//           <p className="upload-message">
//             {videoMessage}
//           </p>
//         )}

//       </div>

//       {false && (
//         <div className="workspace">

//         {/* ========================= */}
//         {/* KNOWLEDGE TREE */}
//         {/* ========================= */}

//         <div className="tree">

//           {hierarchy.map((document) => (
//             <div className="document" key={document.id}>

//               {/* DOCUMENT ROOT */}
//               <div className="node root">
//                 📚 {document.title}
//               </div>

//               {/* TOPICS */}
//               <div className="topics">

//                 {document.topics.map((topic) => {

//                   const topicKey = `${document.id}-${topic.id}`;
//                   const isExpanded = expandedTopics[topicKey];

//                   return (
//                     <div className="topic-container" key={topic.id}>

//                       {/* TOPIC NODE */}
//                       <button
//                         className="node topic"
//                         onClick={() =>
//                           toggleTopic(document.id, topic.id)
//                         }
//                       >
//                         <span className="expand-icon">
//                           {isExpanded ? "▼" : "▶"}
//                         </span>

//                         📘 {topic.name}
//                       </button>

//                       {/* SUBTOPICS */}
//                       {isExpanded && (
//                         <div className="subtopics">

//                           {topic.subtopics.map((subtopic) => (
//                             <button
//                               className={`node subtopic ${
//                                 selectedSubtopic?.id === subtopic.id
//                                   ? "selected"
//                                   : ""
//                               }`}
//                               key={subtopic.id}
//                               onClick={() =>
//                                 setSelectedSubtopic({
//                                   ...subtopic,
//                                   topicName: topic.name,
//                                   documentTitle: document.title,
//                                 })
//                               }
//                             >
//                               📖 {subtopic.name}
//                             </button>
//                           ))}

//                         </div>
//                       )}

//                     </div>
//                   );
//                 })}

//               </div>

//             </div>
//           ))}

//         </div>

//         {/* ========================= */}
//         {/* CONTENT PANEL */}
//         {/* ========================= */}

//         <div className="content-panel">

//           <button
//             className="close-panel-button"
//             onClick={() => {
//               setSelectedSubtopic(null);
//               setAnswer("");
//               setQuestion("");
//             }}
//           >
//             ✕
//           </button>

//           {!selectedSubtopic ? (
//             <div className="empty-state">
//               <div className="empty-icon">📚</div>

//               <h2>Select a topic</h2>

//               <p>
//                 Expand a topic and click a subtopic
//                 to view its study material.
//               </p>
//             </div>
//           ) : (
//             <div className="content">

//               <div className="content-breadcrumb">
//                 <span>📚 {selectedSubtopic.documentTitle}</span>
//                 <span>›</span>
//                 <span>📘 {selectedSubtopic.topicName}</span>
//                 <span>›</span>
//                 <span>📖 {selectedSubtopic.name}</span>
//               </div>

//               <h2>{selectedSubtopic.name}</h2>

//               <div className="chunks">

//                 {selectedSubtopic.chunks?.map((chunk) => (
//                   <div className="chunk-card" key={chunk.id}>

//                     <div className="chunk-label">
//                       STUDY MATERIAL
//                     </div>

//                     <p>{chunk.content}</p>

//                   </div>
//                 ))}

//               </div>

//               <button
//                 className="ask-about-button"
//                 onClick={() => {
//                   setQuestion(
//                     `Explain ${selectedSubtopic.name} based on my study material.`
//                   );
//                 }}
//               >
//                 🤖 Ask AI about this
//               </button>

//               <div className="ai-section">
//                 <h3>🤖 Ask AI about this topic</h3>

//                 <textarea
//                   value={question}
//                   onChange={(e) => setQuestion(e.target.value)}
//                   placeholder={`Ask something about ${selectedSubtopic.name}...`}
//                   rows="4"
//                 />

//                 <button
//                   className="ask-button"
//                   onClick={askAI}
//                   disabled={asking || !question.trim()}
//                 >
//                   {asking ? "Thinking..." : "Ask AI"}
//                 </button>

//                 {answer && (
//                   <div className="ai-answer">
//                     <h3>🤖 AI Answer</h3>
//                     <ReactMarkdown remarkPlugins={[remarkGfm]}>{answer}</ReactMarkdown>
//                   </div>
//                 )}

//               </div>

//             </div>
//           )}

//         </div>

//       </div>
//     )}

//     <div className="knowledge-graph-section">
//         <KnowledgeGraph />
//     </div>

//       {/* Global AI Button */}
//       <button className="global-ai-button" onClick={() => setGlobalAI(!globalAI)}>
//         🤖 Ask AI
//       </button>
//       {globalAI && (
//         <div className="global-ai-chat">

//           <div className="global-ai-header">
//             <div>
//               <strong>🤖 AI Study Assistant</strong>
//               <span>Ask anything about your study material</span>
//             </div>

//             <button
//               className="global-ai-close"
//               onClick={() => setGlobalAI(false)}
//             >
//               ✕
//             </button>
//           </div>

//           <div className="global-ai-body">

//             {!globalAnswer && (
//               <div className="global-ai-welcome">
//                 <div className="global-ai-icon">🤖</div>

//                 <h3>Hey! 👋</h3>

//                 <p>
//                   Ask me anything about your uploaded study material.
//                 </p>
//               </div>
//             )}

//             {globalAnswer && (
//               <div className="global-ai-answer">
//                 <div className="user-question">
//                   <strong>You:</strong>
//                   <p>{globalQuestion}</p>
//                 </div>

//                 <div className="ai-response">
//                   <strong>🤖 AI:</strong>
//                   <ReactMarkdown remarkPlugins={[remarkGfm]}>
//                     {globalAnswer}
//                   </ReactMarkdown>
//                 </div>
//               </div>
//             )}

//           </div>

//           <div className="global-ai-input">

//             <textarea
//               value={globalQuestion}
//               onChange={(e) => setGlobalQuestion(e.target.value)}
//               placeholder="Ask anything..."
//               rows="2"
//               onKeyDown={(e) => {
//                 if (e.key === "Enter" && !e.shiftKey) {
//                   e.preventDefault();
//                   askGlobalAI();
//                 }
//               }}
//             />

//             <button
//               onClick={askGlobalAI}
//               disabled={globalAsking || !globalQuestion.trim()}
//             >
//               {globalAsking ? "..." : "➤"}
//             </button>

//           </div>

//         </div>
//       )}
//     </div>
//   );
// }

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setUploadMessage("Please select at least one file.");
      return;
    }

    setUploading(true);
    setUploadMessage("");

    const formData = new FormData();

    selectedFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      await response.json();

      setUploadMessage(
        "✅ Files uploaded successfully!"
      );

      setSelectedFiles([]);

    } catch (error) {
      console.error(error);

      setUploadMessage(
        "❌ Upload failed. Please try again."
      );

    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="simple-app">

      {/* ========================= */}
      {/* HEADER */}
      {/* ========================= */}

      <header className="simple-header">
        <h1>AI Education System</h1>
        <p>DAA Knowledge Graph</p>
      </header>

      {/* ========================= */}
      {/* UPLOAD NOTES */}
      {/* ========================= */}

      <section className="simple-upload-section">

        <h2>📤 Upload Study Material</h2>

        <p>
          Upload DAA notes to process the study material.
        </p>

        <input
          type="file"
          accept=".pdf,.pptx"
          multiple
          onChange={(event) =>
            setSelectedFiles(
              Array.from(event.target.files)
            )
          }
        />

        {selectedFiles.length > 0 && (
          <div className="selected-files">

            {selectedFiles.map((file) => (
              <div key={file.name}>
                📄 {file.name}
              </div>
            ))}

          </div>
        )}

        <button
          className="upload-button"
          onClick={handleUpload}
          disabled={uploading}
        >
          {uploading
            ? "Processing..."
            : "Upload Notes"}
        </button>

        {uploadMessage && (
          <p className="upload-message">
            {uploadMessage}
          </p>
        )}

      </section>

      {/* ========================= */}
      {/* KNOWLEDGE GRAPH */}
      {/* ========================= */}

      <main className="full-graph-area">
        <KnowledgeGraph />
      </main>

    </div>
  );
}

export default App;